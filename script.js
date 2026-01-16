const chatLog = document.getElementById("chat-log");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

const thinkingEl = document.createElement("div");
thinkingEl.innerHTML = `<strong>Bot:</strong> <span class="thinking">🤖 Thinking longer to give a better answer
<span class="dots"></span></span>`;
thinkingEl.style.display = "none";
chatLog.appendChild(thinkingEl);

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;


    userInput.value = "";

    addMessage("You", message);

    thinkingEl.style.display = "block";

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt: message })
        });
        const data = await response.json();

        thinkingEl.style.display = "none";
        addMessage("Bot", data.reply);
        chatLog.scrollTop = chatLog.scrollHeight;
    } catch (err) {
        thinkingEl.style.display = "none";
        addMessage("Bot", "Error: " + err.message);
    }
}

function addMessage(sender, text) {
    const msgDiv = document.createElement("div");
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatLog.appendChild(msgDiv);
}

const style = document.createElement('style');
style.innerHTML = `
.thinking .dots::after {
    content: '';
    animation: dots 1.5s steps(3, end) infinite;
}

@keyframes dots {
    0% { content: ''; }
    33% { content: '.'; }
    66% { content: '..'; }
    100% { content: '...'; }
}
`;
document.head.appendChild(style);
