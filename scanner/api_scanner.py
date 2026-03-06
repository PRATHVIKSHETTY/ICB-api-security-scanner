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

# Default headers
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
            pass

    return allowed


def scan_api(input_text):

    url = validate_url(extract_url(input_text))

    report = {
        "api_url": url,
        "status_code": None,
        "response_time_ms": None,
        "allowed_methods": [],
        "header_issues": [],
        "authentication_issue": None,
        "rate_limit_issue": None,
        "server_information": None
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

        # Status check
        report["status_code"] = check_status_code(response)

        # Header security check
        report["header_issues"] = check_headers(response)

        # Authentication check
        report["authentication_issue"] = check_authentication(
            url, DEFAULT_HEADERS
        )

        # Rate limit check
        report["rate_limit_issue"] = check_rate_limit(
            url, DEFAULT_HEADERS
        )

        # Server info
        report["server_information"] = check_server_info(response)

        # HTTP method discovery
        report["allowed_methods"] = discover_methods(url)

        return report

    except requests.exceptions.RequestException as e:

        return {
            "api_url": url,
            "status_code": "Scan failed",
            "response_time_ms": None,
            "allowed_methods": [],
            "header_issues": [],
            "authentication_issue": "Scan failed",
            "rate_limit_issue": "Scan failed",
            "server_information": str(e)
        }


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