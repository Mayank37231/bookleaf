const form = document.querySelector("#chatForm");
const queryInput = document.querySelector("#queryInput");
const emailInput = document.querySelector("#emailInput");
const channelInput = document.querySelector("#channelInput");
const messages = document.querySelector("#messages");

document.querySelectorAll("[data-query]").forEach((button) => {
    button.addEventListener("click", () => {
        queryInput.value = button.dataset.query;
        queryInput.focus();
    });
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;
    addMessage(query, "user");
    queryInput.value = "";
    const pending = addMessage("Checking author records and knowledge base...", "bot");

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                query,
                email: emailInput.value.trim(),
                channel: channelInput.value,
            }),
        });
        const data = await response.json();
        pending.remove();
        addMessage(data.response || data.error, "bot", data);
    } catch (error) {
        pending.remove();
        addMessage("The API could not be reached. Please check the Django server.", "bot", {escalated: true});
    }
});

function addMessage(text, type, data = null) {
    const el = document.createElement("div");
    el.className = `message ${type}`;
    const p = document.createElement("p");
    p.textContent = text;
    el.appendChild(p);

    if (data && data.intent) {
        const meta = document.createElement("div");
        meta.className = "meta";
        meta.appendChild(badge(data.intent.replaceAll("_", " ")));
        meta.appendChild(badge(`${Math.round(data.confidence * 100)}% confidence`, data.escalated ? "warn" : ""));
        if (data.escalated) meta.appendChild(badge("escalated", "danger"));
        if (data.author) meta.appendChild(badge(data.author.bookTitle));
        el.appendChild(meta);
    }

    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
    return el;
}

function badge(text, tone = "") {
    const el = document.createElement("span");
    el.className = `badge ${tone}`;
    el.textContent = text;
    return el;
}
