import os
from google import genai

# Create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_chatbot_response(message, scan_report=None):

    if not message:
        return "Please ask a question."

    try:

        context = ""
        if scan_report:
            context = f"\nAPI Scan Report:\n{scan_report}"

        prompt = f"""
You are a cybersecurity expert helping developers secure APIs.

User question:
{message}

{context}

Explain clearly and give practical security recommendations.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"AI error: {str(e)}"