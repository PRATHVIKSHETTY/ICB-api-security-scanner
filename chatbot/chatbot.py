import ollama


def get_chatbot_response(message, history=None, scan_report=None):

    if not message:
        return "Please ask a question."

    try:

        history_text = ""

        if history:
            history = history[-3:]
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"

        context = ""
        if scan_report:
            context = f"\nAPI Scan Findings:\n{scan_report}"

        prompt = f"""
You are an API security assistant.

Explain API vulnerabilities clearly in 2-3 sentences.

Conversation:
{history_text}

User question:
{message}

{context}
"""

        response = ollama.chat(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"].strip()

    except Exception as e:

        print("Ollama error:", e)

        return "The AI assistant is currently unavailable."