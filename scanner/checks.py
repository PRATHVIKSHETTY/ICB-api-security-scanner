import requests
import time


def check_headers(response):

    required_headers = [
        "X-Frame-Options",
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "Strict-Transport-Security",
        "Referrer-Policy"
    ]

    issues = []

    for header in required_headers:
        if header not in response.headers:
            issues.append(f"Missing security header: {header}")

    return issues


def check_status_code(response):

    if response.status_code >= 500:
        return "Server error detected"

    if response.status_code == 200:
        return "API reachable"

    return f"Unexpected status code: {response.status_code}"


def check_authentication(url):

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            return "API accessible without authentication"

        if response.status_code == 401:
            return "Authentication required"

        return "Authentication behavior unclear"

    except Exception:
        return "Authentication test failed"


def check_rate_limit(url):

    try:
        responses = []

        for i in range(5):
            r = requests.get(url, timeout=5)
            responses.append(r.status_code)
            time.sleep(0.2)

        if all(code == 200 for code in responses):
            return "Possible missing rate limiting"

        return "Rate limiting detected"

    except Exception:
        return "Rate limit test failed"


def check_server_info(response):

    if "Server" in response.headers:
        return f"Server header exposed: {response.headers['Server']}"

    return "Server information hidden"