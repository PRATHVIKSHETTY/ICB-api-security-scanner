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
    check_server_info,
    check_cors,
    check_sensitive_data,
    check_api_keys
)

DEFAULT_HEADERS = {
    "User-Agent": "API-Security-Scanner/1.0",
    "Accept": "application/json",
    "Connection": "close"
}


def extract_url(text):
    """Extract URL from curl / wget / raw text"""

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
    """Generate realistic API security score"""

    score = 100

    # Header issues
    if report.get("header_issues"):
        score -= min(len(report["header_issues"]) * 5, 15)

    # Authentication issue
    if report.get("authentication_issue"):
        if "without authentication" in report["authentication_issue"].lower():
            score -= 20

    # Rate limiting
    if report.get("rate_limit_issue"):
        if "no rate limiting" in report["rate_limit_issue"].lower():
            score -= 25

    # Server exposure
    if report.get("server_information"):
        if "server exposed" in report["server_information"].lower():
            score -= 5

    # Sensitive data leak
    if report.get("sensitive_data"):
        score -= 20

    # API key leak
    if report.get("api_key_exposure"):
        score -= 30

    # HTTP error
    if report.get("status_code", 0) >= 400:
        score -= 15

    # Slow response
    if report.get("response_time_ms", 0) > 2000:
        score -= 5

    return max(score, 0)


def count_security_checks(report):
    """Count passed security checks"""

    total_checks = 7
    passed = 0

    # Headers
    if not report["header_issues"]:
        passed += 1

    # Authentication
    if "required" in report["authentication_issue"].lower():
        passed += 1

    # Rate limiting
    if "detected" in report["rate_limit_issue"].lower():
        passed += 1

    # Server hidden
    if "hidden" in report["server_information"].lower():
        passed += 1

    # CORS
    if not report.get("cors_issues"):
        passed += 1

    # Sensitive data
    if not report.get("sensitive_data"):
        passed += 1

    # API keys
    if not report.get("api_key_exposure"):
        passed += 1

    return passed, total_checks


def generate_test_results(report):
    """Generate pass/fail results for each security test"""

    results = []

    results.append({
        "test": "Security Headers",
        "status": "Passed" if not report["header_issues"] else "Failed"
    })

    results.append({
        "test": "Authentication Protection",
        "status": "Passed" if "required" in report["authentication_issue"].lower() else "Failed"
    })

    results.append({
        "test": "Rate Limiting",
        "status": "Passed" if "detected" in report["rate_limit_issue"].lower() else "Failed"
    })

    results.append({
        "test": "Server Information Hidden",
        "status": "Passed" if "hidden" in report["server_information"].lower() else "Warning"
    })

    results.append({
        "test": "CORS Configuration",
        "status": "Passed" if not report.get("cors_issues") else "Failed"
    })

    results.append({
        "test": "Sensitive Data Exposure",
        "status": "Passed" if not report.get("sensitive_data") else "Failed"
    })

    results.append({
        "test": "API Key Exposure",
        "status": "Passed" if not report.get("api_key_exposure") else "Failed"
    })

    return results


def get_status_label(status_code):
    """Convert HTTP status code to readable label"""

    if status_code == 200:
        return "Healthy"

    elif 200 < status_code < 400:
        return "Redirect"

    elif status_code >= 400:
        return "Error"

    return "Unknown"


def scan_api(input_text):

    url = validate_url(extract_url(input_text))

    report = {
        "api_url": url,
        "status_code": 0,
        "status_message": "",
        "status": "Unknown",
        "response_time_ms": 0,
        "allowed_methods": [],
        "header_issues": [],
        "cors_issues": [],
        "sensitive_data": [],
        "api_key_exposure": [],
        "authentication_issue": "",
        "rate_limit_issue": "",
        "server_information": "",
        "security_score": 100,
        "checks_passed": 0,
        "total_checks": 7,
        "test_results": []
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

        report["status"] = get_status_label(response.status_code)

        report["header_issues"] = check_headers(response) or []

        report["cors_issues"] = check_cors(response) or []

        report["sensitive_data"] = check_sensitive_data(response) or []

        report["api_key_exposure"] = check_api_keys(response) or []

        report["authentication_issue"] = check_authentication(url, DEFAULT_HEADERS) or ""

        report["rate_limit_issue"] = check_rate_limit(url, DEFAULT_HEADERS) or ""

        report["server_information"] = check_server_info(response) or ""

        report["allowed_methods"] = discover_methods(url)

        # Security score
        report["security_score"] = calculate_security_score(report)

        # Count checks
        passed, total = count_security_checks(report)
        report["checks_passed"] = passed
        report["total_checks"] = total

        # Individual results
        report["test_results"] = generate_test_results(report)

    except requests.exceptions.Timeout:

        report["status_message"] = "Connection timed out"
        report["server_information"] = "Timeout while connecting"
        report["security_score"] = 0
        report["status"] = "Error"

    except requests.exceptions.ConnectionError:

        report["status_message"] = "Connection failed"
        report["server_information"] = "Could not reach API server"
        report["security_score"] = 0
        report["status"] = "Error"

    except requests.exceptions.RequestException as e:

        report["status_message"] = "Scan error"
        report["server_information"] = str(e)
        report["security_score"] = 0
        report["status"] = "Error"

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