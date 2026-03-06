import requests
import json
import os

from scanner.checks import (
    check_headers,
    check_status_code,
    check_authentication,
    check_rate_limit,
    check_server_info
)


def scan_api(url):

    report = {
        "api_url": url,
        "status_code": None,
        "header_issues": [],
        "authentication_issue": None,
        "rate_limit_issue": None,
        "server_information": None
    }

    try:
        response = requests.get(url, timeout=5)

        # Basic API status
        report["status_code"] = check_status_code(response)

        # Run security checks
        report["header_issues"] = check_headers(response)
        report["authentication_issue"] = check_authentication(url)
        report["rate_limit_issue"] = check_rate_limit(url)
        report["server_information"] = check_server_info(response)

        return report

    except Exception as e:
        return {"error": str(e)}


def save_report(report):

    try:
        os.makedirs("reports", exist_ok=True)

        with open("reports/report.json", "w") as file:
            json.dump(report, file, indent=4)

    except Exception as e:
        print("Error saving report:", e)