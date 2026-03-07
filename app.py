from flask import Flask, render_template, request, jsonify, send_file
from scanner.pdf_report import generate_pdf
from scanner.api_scanner import scan_api, save_report
from chatbot.chatbot import get_chatbot_response
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# store latest scan result
last_scan_report = None

# store scan history
scan_history = []


# HOME DASHBOARD
@app.route("/")
def home():

    total_scans = len(scan_history)

    vulnerabilities = sum(scan["issues"] for scan in scan_history)

    secure = sum(1 for scan in scan_history if scan["issues"] == 0)

    security_score = 100
    if total_scans > 0:
        security_score = max(0, 100 - vulnerabilities * 10)

    stats = {
        "total_scans": total_scans,
        "vulnerabilities": vulnerabilities,
        "secure": secure,
        "security_score": security_score
    }

    return render_template(
        "index.html",
        stats=stats,
        recent_scans=scan_history
    )


# SCAN API
@app.route("/scan", methods=["POST"])
def scan():

    global last_scan_report
    global scan_history

    api_url = request.form.get("api_url")

    if not api_url:
        return render_template("index.html", error="Please enter an API URL")

    try:

        report = scan_api(api_url)

        save_report(report)

        last_scan_report = report

        issues = len(report.get("header_issues", []))

        if report.get("rate_limiting") == "No rate limiting detected":
            issues += 1

        if report.get("authentication") == "API accessible without authentication":
            issues += 1

        risk = "Low"

        if issues >= 3:
            risk = "High"
        elif issues == 2:
            risk = "Medium"

        scan_history.append({
            "url": api_url,
            "status": report.get("status", "Unknown"),
            "issues": issues,
            "risk": risk
        })

        # keep only last 10 scans
        scan_history = scan_history[-10:]

        return render_template("result.html", report=report)

    except Exception as e:
        return render_template("index.html", error=str(e))


# CHATBOT
@app.route("/chat", methods=["POST"])
def chat():

    global last_scan_report

    data = request.get_json()

    if not data:
        return jsonify({"reply": "Please enter a message."})

    user_message = data.get("message")
    history = data.get("history", [])

    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    try:

        response = get_chatbot_response(
            user_message,
            history=history,
            scan_report=last_scan_report
        )

        return jsonify({"reply": response})

    except Exception as e:
        print("Chat error:", e)

        return jsonify({
            "reply": "Assistant failed to respond."
        })


# CHATBOT PAGE
@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


# DOWNLOAD REPORT
@app.route("/download-report")
def download_report():

    global last_scan_report

    if not last_scan_report:
        return "No report generated yet."

    pdf = generate_pdf(last_scan_report)

    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="api_security_report.pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)