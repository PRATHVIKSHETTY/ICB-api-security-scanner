import requests
import time
import re

DEFAULT_HEADERS = {
    "User-Agent": "API-Security-Scanner/1.0",
    "Accept": "application/json"
}


def check_headers(response):
    """Check for missing important security headers"""

    required_headers = [
        "X-Frame-Options",
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "Strict-Transport-Security",
        "Referrer-Policy"
    ]

    issues = []

    headers = {k.lower(): v for k, v in response.headers.items()}

    for header in required_headers:
        if header.lower() not in headers:
            issues.append(f"Missing security header: {header}")

    # Return empty list if no issues
    return issues


def check_status_code(response):
    """Evaluate API response status"""

    code = response.status_code

    if code >= 500:
        return f"Server error ({code})"

    elif code >= 400:
        return f"Client error ({code})"

    elif code >= 300:
        return f"Redirect detected ({code})"

    elif code == 200:
        return "API reachable (200 OK)"

    return f"Status code: {code}"


def check_authentication(url, headers=DEFAULT_HEADERS):
    """Detect if API requires authentication"""

    try:

        r = requests.get(url, headers=headers, timeout=5)

        if r.status_code == 401:
            return "Authentication required"

        if r.status_code == 403:
            return "Access forbidden (authentication likely required)"

        if r.status_code == 200:
            return "API accessible without authentication"

        return f"Authentication behavior unclear ({r.status_code})"

    except requests.exceptions.RequestException as e:
        return f"Authentication test failed: {str(e)}"


def check_rate_limit(url, headers=DEFAULT_HEADERS):
    """Detect basic rate limiting"""

    try:

        responses = []
        last_response = None

        for _ in range(5):

            r = requests.get(url, headers=headers, timeout=5)

            responses.append(r.status_code)
            last_response = r

            time.sleep(0.2)

        if 429 in responses:
            return "Rate limiting detected (429 Too Many Requests)"

        if last_response:
            if (
                "X-RateLimit-Limit" in last_response.headers
                or "RateLimit-Limit" in last_response.headers
            ):
                return "Rate limiting detected (header based)"

        return "No rate limiting detected"

    except requests.exceptions.RequestException as e:
        return f"Rate limit test failed: {str(e)}"


def check_server_info(response):
    """Detect server technology exposure"""

    server = response.headers.get("Server")

    if server:
        return f"Server exposed: {server}"

    return "Server information hidden"


def check_cors(response):
    """Detect dangerous CORS configurations"""

    issues = []

    origin = response.headers.get("Access-Control-Allow-Origin")

    if origin == "*":
        issues.append("CORS misconfiguration: Access-Control-Allow-Origin set to *")

    return issues


def check_sensitive_data(response):
    """Detect possible sensitive data exposure"""

    issues = []

    try:

        text = response.text.lower()

        keywords = [
            "password",
            "secret",
            "token",
            "api_key",
            "private_key"
        ]

        for key in keywords:
            if key in text:
                issues.append(f"Sensitive data detected in response: {key}")

    except Exception:
        pass

    return issues


def check_api_keys(response):
    """Detect exposed API keys in response"""

    issues = []

    patterns = [
        r"AIza[0-9A-Za-z-_]{35}",   # Google API keys
        r"sk_live_[0-9a-zA-Z]{24}", # Stripe
        r"ghp_[0-9A-Za-z]{36}",     # GitHub
    ]

    text = response.text

    for pattern in patterns:
        if re.search(pattern, text):
            issues.append("Possible API key exposed in response")

    return issues