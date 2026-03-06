from flask import Flask, render_template, request, jsonify, send_file
from scanner.pdf_report import generate_pdf
from scanner.api_scanner import scan_api, save_report
from chatbot.chatbot import get_chatbot_response
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

last_scan_report = None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():

    global last_scan_report

    api_url = request.form.get("api_url")

    if not api_url:
        return render_template("index.html", error="Please enter an API URL")

    try:

        report = scan_api(api_url)

        save_report(report)

        last_scan_report = report

        return render_template("result.html", report=report)

    except Exception as e:
        return render_template("index.html", error=str(e))


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"reply": "Please enter a message."})

    user_message = data["message"]

    response = get_chatbot_response(user_message)

    return jsonify({"reply": response})


@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


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