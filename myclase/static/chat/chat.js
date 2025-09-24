document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");

    if (!chatForm || !chatInput || !chatMessages) return;

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const roomId = chatForm.querySelector("input[name='room_id']").value;
        const content = chatInput.value.trim();
        if (!content) return;

        fetch("/chat/send/", {
            method: "POST",
            headers: {
                "X-CSRFToken": chatForm.querySelector("[name=csrfmiddlewaretoken]").value,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `room_id=${roomId}&content=${encodeURIComponent(content)}`
        })
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                const div = document.createElement("div");
                div.classList.add("message", "sent");
                div.innerHTML = `<strong>${data.sender}</strong>: ${data.content} <span class="time">${data.timestamp}</span>`;
                chatMessages.appendChild(div);
                chatInput.value = "";
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        })
        .catch(console.error);
    });
});
