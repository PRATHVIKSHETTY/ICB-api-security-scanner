import os
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("Loaded Gemini Key:", os.getenv("GEMINI_API_KEY"))
if not api_key:
    raise ValueError("GEMINI_API_KEY not set. Add it to your .env file.")

client = genai.Client(api_key=api_key)


def get_chatbot_response(message, history=None, scan_report=None):

    if not message:
        return "Please ask a question."

    try:

        # limit chat history to last 3 messages to reduce token usage
        history_text = ""
        if history:
            history = history[-3:]
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"

        # include scan report context (shortened)
        context = ""
        if scan_report:
            context = f"\nAPI Scan Findings:\n{scan_report}"

        prompt = f"""
You are an API security assistant helping developers understand API vulnerabilities.

Keep responses short (2–3 sentences).

Conversation:
{history_text}

User question:
{message}

{context}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        reply = response.text

        if not reply:
            return "I couldn't generate a response."

        return reply.strip()

    except Exception as e:

        print("Gemini error:", e)

        error_text = str(e)

        # Handle rate limits
        if "429" in error_text:
            return "The AI assistant is temporarily busy due to API limits. Please try again in a few seconds."

        # fallback answers for common questions
        message_lower = message.lower()

        if "rate limit" in message_lower:
            return "Rate limiting restricts how many requests a client can send to an API within a time window. Without it, attackers can perform brute-force or denial-of-service attacks."

        if "cors" in message_lower:
            return "CORS (Cross-Origin Resource Sharing) controls which domains can access an API from a browser. Misconfigured CORS can expose sensitive endpoints to malicious websites."

        if "authentication" in message_lower:
            return "Broken authentication occurs when APIs fail to properly verify users, allowing attackers to access accounts or sensitive data."

        return "The assistant is currently unavailable. Please try again later."