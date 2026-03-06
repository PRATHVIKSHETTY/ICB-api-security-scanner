function sendMessage() {

    const message = document.getElementById("message").value;

    if (!message) {
        return;
    }

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("chat-response").innerText = data.reply;
    })
    .catch(error => {
        document.getElementById("chat-response").innerText = "Chatbot error.";
    });

}