from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime


def generate_pdf(report):

    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "API Security Scan Report")

    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated: {datetime.now()}")

    y -= 40

    def write_line(text):
        nonlocal y
        c.drawString(50, y, text)
        y -= 20

    write_line(f"API URL: {report.get('api_url')}")
    write_line(f"Status: {report.get('status_code')}")
    write_line(f"Response Time: {report.get('response_time_ms')} ms")

    y -= 10
    write_line("Allowed Methods:")

    for method in report.get("allowed_methods", []):
        write_line(f" - {method}")

    y -= 10
    write_line("Header Issues:")

    for issue in report.get("header_issues", []):
        write_line(f" - {issue}")

    y -= 10
    write_line(f"Authentication: {report.get('authentication_issue')}")
    write_line(f"Rate Limit: {report.get('rate_limit_issue')}")
    write_line(f"Server Info: {report.get('server_information')}")

    c.save()

    buffer.seek(0)

    return buffer