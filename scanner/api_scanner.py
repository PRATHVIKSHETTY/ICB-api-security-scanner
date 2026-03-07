import requests
import json
import os
import re
import time

from scanner.checks import (
    check_headers,
    check_status_code,
    check_authentication,
    check_rate_limit,
    check_server_info
)


DEFAULT_HEADERS = {
    "User-Agent": "API-Security-Scanner/1.0",
    "Accept": "application/json",
    "Connection": "close"
}


def extract_url(text):
    """Extract URL from curl / wget / httpie / raw text"""

    match = re.search(r"https?://[^\s]+", text)

    if match:
        return match.group(0)

    return text.strip()


def validate_url(url):
    """Ensure URL contains protocol"""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def discover_methods(url):
    """Check allowed HTTP methods"""

    methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    allowed = []

    for method in methods:

        try:
            r = requests.request(
                method,
                url,
                headers=DEFAULT_HEADERS,
                timeout=5
            )

            if r.status_code not in [405, 501]:
                allowed.append(method)

        except requests.exceptions.RequestException:
            continue

    return allowed


def calculate_security_score(report):
    """Generate security score out of 100"""

    score = 100

    # header issues
    if report["header_issues"]:
        score -= min(len(report["header_issues"]) * 10, 30)

    # authentication risk
    if report["authentication_issue"]:
        if "without authentication" in report["authentication_issue"].lower():
            score -= 25

    # rate limit issue
    if report["rate_limit_issue"]:
        if "no rate limiting" in report["rate_limit_issue"].lower():
            score -= 15

    # bad status codes
    if report["status_code"] >= 400:
        score -= 20

    return max(score, 0)


def scan_api(input_text):

    url = validate_url(extract_url(input_text))

    report = {
        "api_url": url,
        "status_code": 0,
        "status_message": "",
        "response_time_ms": 0,
        "allowed_methods": [],
        "header_issues": [],
        "authentication_issue": "",
        "rate_limit_issue": "",
        "server_information": "",
        "security_score": 100
    }

    try:

        start = time.time()

        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=10,
            allow_redirects=True
        )

        end = time.time()

        report["response_time_ms"] = round((end - start) * 1000, 2)

        report["status_code"] = response.status_code

        report["status_message"] = check_status_code(response)

        report["header_issues"] = check_headers(response) or []

        report["authentication_issue"] = check_authentication(
            url, DEFAULT_HEADERS
        ) or ""

        report["rate_limit_issue"] = check_rate_limit(
            url, DEFAULT_HEADERS
        ) or ""

        report["server_information"] = check_server_info(response) or ""

        report["allowed_methods"] = discover_methods(url)

        # Calculate score
        report["security_score"] = calculate_security_score(report)

    except requests.exceptions.Timeout:

        report["status_message"] = "Connection timed out"
        report["server_information"] = "Timeout while connecting"
        report["security_score"] = 0

    except requests.exceptions.ConnectionError:

        report["status_message"] = "Connection failed"
        report["server_information"] = "Could not reach API server"
        report["security_score"] = 0

    except requests.exceptions.RequestException as e:

        report["status_message"] = "Scan error"
        report["server_information"] = str(e)
        report["security_score"] = 0

    return report


def save_report(report):
    """Save scan result"""

    try:

        os.makedirs("reports", exist_ok=True)

        report_file = os.path.join("reports", "report.json")

        with open(report_file, "w") as f:
            json.dump(report, f, indent=4)

        print("Report saved:", report_file)

    except Exception as e:
        print("Error saving report:", e)