let chatHistory = [];


/* ---------- Render Message ---------- */
function appendMessage(text, from) {

    const messages = document.getElementById("chatMessages");
    if (!messages) return;

    const row = document.createElement("div");
    row.className = "message-row " + (from === "user" ? "user" : "bot");

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (!text) text = "No response from assistant.";

    // Markdown rendering if library exists
    if (typeof marked !== "undefined") {
        bubble.innerHTML = marked.parse(text);
    } else {
        bubble.innerHTML = String(text).replace(/\n/g, "<br>");
    }

    row.appendChild(bubble);
    messages.appendChild(row);

    messages.scrollTop = messages.scrollHeight;
}


/* ---------- Typing Indicator ---------- */
function showTyping() {

    const messages = document.getElementById("chatMessages");
    if (!messages) return;

    const row = document.createElement("div");
    row.className = "message-row bot";
    row.id = "typing-indicator";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerText = "Assistant is typing...";

    row.appendChild(bubble);
    messages.appendChild(row);

    messages.scrollTop = messages.scrollHeight;
}


function removeTyping() {

    const typing = document.getElementById("typing-indicator");
    if (typing) typing.remove();

}


/* ---------- Send Message ---------- */
function sendMessage() {

    const input = document.getElementById("message");
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, "user");

    chatHistory.push({
        role: "user",
        content: message
    });

    input.value = "";

    showTyping();

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message,
            history: chatHistory
        })
    })
    .then(res => res.json())
    .then(data => {

        removeTyping();

        const reply = data.reply || "Sorry, I couldn't understand that.";

        appendMessage(reply, "bot");

        chatHistory.push({
            role: "assistant",
            content: reply
        });

    })
    .catch(() => {

        removeTyping();

        appendMessage(
            "⚠️ Unable to contact the AI assistant. Please try again.",
            "bot"
        );

    });
}


/* ---------- Enter Key Support ---------- */
function handleKeyPress(event) {

    if (event.key === "Enter") {

        event.preventDefault();
        sendMessage();

    }
}

/* ---------- Toggle Chat Panel ---------- */
function toggleChat() {

    const panel = document.getElementById("chatPanel");
    const layout = document.querySelector(".page-layout");

    panel.classList.toggle("open");
    layout.classList.toggle("chat-open");

}