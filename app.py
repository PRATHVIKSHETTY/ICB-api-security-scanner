from flask import Flask, render_template, request, jsonify
from scanner.api_scanner import scan_api, save_report
from chatbot.chatbot import get_chatbot_response
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# API Scanner
@app.route("/scan", methods=["POST"])
def scan():

    api_url = request.form.get("api_url")

    if not api_url:
        return render_template("index.html", error="Please enter an API URL")

    try:
        report = scan_api(api_url)
        save_report(report)

        return render_template("result.html", report=report)

    except Exception as e:
        return render_template("index.html", error=str(e))


# Chatbot API
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"reply": "Please enter a message."})

    user_message = data["message"]

    response = get_chatbot_response(user_message)

    return jsonify({"reply": response})


# Optional chatbot page
@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


if __name__ == "__main__":
    app.run(debug=True)