// -----------------------------------
// CONFIG
// -----------------------------------

const API_BASE = "http://localhost:8000/api";

// -----------------------------------
// STATE
// -----------------------------------

let isLoading = false;


// -----------------------------------
// DOM ELEMENTS
// -----------------------------------

const chat = document.getElementById("chat");
const input = document.getElementById("input");


// -----------------------------------
// MESSAGE RENDERING
// -----------------------------------

function createMessage(role, text) {
    const div = document.createElement("div");
    div.className = `message ${role}`;

    div.innerHTML = `
        <div class="bubble">
            <strong>${role.toUpperCase()}:</strong>
            <span>${escapeHTML(text)}</span>
        </div>
    `;

    chat.appendChild(div);
    scrollToBottom();
}

function escapeHTML(str) {
    return str.replace(/[&<>"']/g, (tag) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    }[tag]));
}


// -----------------------------------
// UX HELPERS
// -----------------------------------

function scrollToBottom() {
    chat.scrollTop = chat.scrollHeight;
}

function setLoading(state) {
    isLoading = state;
    input.disabled = state;

    if (state) {
        showTypingIndicator();
    } else {
        removeTypingIndicator();
    }
}


// -----------------------------------
// TYPING INDICATOR
// -----------------------------------

let typingEl = null;

function showTypingIndicator() {
    typingEl = document.createElement("div");
    typingEl.className = "message ai typing";
    typingEl.innerHTML = `<div class="bubble">JARVIS is thinking...</div>`;
    chat.appendChild(typingEl);
    scrollToBottom();
}

function removeTypingIndicator() {
    if (typingEl) {
        typingEl.remove();
        typingEl = null;
    }
}


// -----------------------------------
// API LAYER
// -----------------------------------

async function sendToAPI(message) {
    const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message })
    });

    if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
    }

    return await res.json();
}


// -----------------------------------
// MAIN SEND FUNCTION
// -----------------------------------

async function sendMessage() {
    const text = input.value.trim();

    if (!text || isLoading) return;

    createMessage("user", text);
    input.value = "";

    setLoading(true);

    try {
        const data = await sendToAPI(text);

        createMessage("ai", data.response || "No response");

    } catch (err) {
        console.error(err);
        createMessage("error", "Failed to connect to JARVIS backend.");
    }

    setLoading(false);
}


// -----------------------------------
// EVENT LISTENERS
// -----------------------------------

document.querySelector("button").addEventListener("click", sendMessage);

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});


// -----------------------------------
// INIT
// -----------------------------------

createMessage("system", "JARVIS Web Interface Initialized");