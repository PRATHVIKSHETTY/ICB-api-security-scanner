def get_chatbot_response(message):

    if not message:
        return "Please ask a question about API security."

    message = message.lower()

    # Authentication
    if "authentication" in message or "auth" in message:
        return (
            "APIs should require authentication to prevent unauthorized access. "
            "Common methods include API keys, OAuth, and JWT tokens."
        )

    # Rate limiting
    if "rate limit" in message or "rate limiting" in message:
        return (
            "Rate limiting prevents abuse by restricting how many requests "
            "a user can send in a given time period."
        )

    # Headers
    if "header" in message or "security header" in message:
        return (
            "Security headers help protect APIs and web applications. "
            "Important headers include Content-Security-Policy, "
            "X-Frame-Options, and X-Content-Type-Options."
        )

    # Server info
    if "server" in message:
        return (
            "Server information in HTTP headers can reveal technology "
            "details to attackers. It is recommended to hide or minimize "
            "server version information."
        )

    # API security
    if "api security" in message or "secure api" in message:
        return (
            "To secure APIs you should implement authentication, "
            "rate limiting, input validation, HTTPS encryption, "
            "and proper security headers."
        )

    # Vulnerabilities
    if "vulnerability" in message or "risk" in message:
        return (
            "Common API vulnerabilities include missing authentication, "
            "exposed data, lack of rate limiting, and insecure headers."
        )

    # Help
    if "help" in message:
        return (
            "You can ask questions about API authentication, rate limiting, "
            "security headers, vulnerabilities, or best practices."
        )

    # Default fallback
    return (
        "I can help explain API security issues such as authentication, "
        "rate limiting, security headers, and vulnerabilities."
    )