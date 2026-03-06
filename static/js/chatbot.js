function appendMessage(text, from) {
    const messages = document.getElementById('chatMessages');
    if (!messages) return;

    const row = document.createElement('div');
    row.className = 'message-row ' + (from === 'user' ? 'user' : 'bot');

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;

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
    input.value = '';

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        appendMessage(data.reply || 'No response from assistant.', 'bot');
    })
    .catch(() => {
        appendMessage('Sorry, something went wrong while contacting the assistant.', 'bot');
    });
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
}
