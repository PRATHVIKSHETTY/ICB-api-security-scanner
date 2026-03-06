let chatHistory = [];

function appendMessage(text, from) {

    const messages = document.getElementById('chatMessages');
    if (!messages) return;

    const row = document.createElement('div');
    row.className = 'message-row ' + (from === 'user' ? 'user' : 'bot');

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    if (!text) text = "No response from assistant.";

    bubble.innerHTML = String(text).replace(/\n/g, "<br>");

    row.appendChild(bubble);
    messages.appendChild(row);

    messages.scrollTop = messages.scrollHeight;
}

function sendMessage() {

    const input = document.getElementById('message');
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, 'user');

    // store user message
    chatHistory.push({
        role: "user",
        content: message
    });

    input.value = '';

    // typing indicator
    appendMessage("Assistant is typing...", "bot");

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            history: chatHistory
        })
    })
    .then(res => res.json())
    .then(data => {

        const messages = document.getElementById('chatMessages');

        // remove typing indicator
        if (messages.lastChild) {
            messages.removeChild(messages.lastChild);
        }

        const reply = data.reply || "Sorry, I couldn't understand that.";

        appendMessage(reply, 'bot');

        // store assistant reply
        chatHistory.push({
            role: "assistant",
            content: reply
        });

    })
    .catch(() => {

        const messages = document.getElementById('chatMessages');

        if (messages.lastChild) {
            messages.removeChild(messages.lastChild);
        }

        appendMessage(
            "Sorry, something went wrong while contacting the assistant.",
            'bot'
        );
    });
}

function handleKeyPress(event) {

    if (event.key === 'Enter') {

        event.preventDefault();
        sendMessage();

    }
}