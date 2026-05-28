const logsBody = document.querySelector("#logsBody");
const intentFilter = document.querySelector("#intentFilter");
const escalatedFilter = document.querySelector("#escalatedFilter");
const totalLogs = document.querySelector("#totalLogs");
const escalatedLogs = document.querySelector("#escalatedLogs");
const avgConfidence = document.querySelector("#avgConfidence");

intentFilter.addEventListener("change", loadLogs);
escalatedFilter.addEventListener("change", loadLogs);
loadLogs();

async function loadLogs() {
    const params = new URLSearchParams();
    if (intentFilter.value) params.set("intent", intentFilter.value);
    if (escalatedFilter.value) params.set("escalated", escalatedFilter.value);
    const response = await fetch(`/api/logs?${params.toString()}`);
    const data = await response.json();
    renderLogs(data.logs);
}

function renderLogs(logs) {
    totalLogs.textContent = logs.length;
    escalatedLogs.textContent = logs.filter((log) => log.escalated).length;
    const avg = logs.length ? logs.reduce((sum, log) => sum + log.confidence, 0) / logs.length : 0;
    avgConfidence.textContent = `${Math.round(avg * 100)}%`;
    logsBody.innerHTML = logs.map((log) => `
        <tr>
            <td>${new Date(log.createdAt).toLocaleString()}</td>
            <td>${escapeHtml(log.query)}</td>
            <td>${log.intent.replaceAll("_", " ")}</td>
            <td>${Math.round(log.confidence * 100)}%</td>
            <td><span class="badge ${log.escalated ? "danger" : ""}">${log.escalated ? "Escalated" : "Resolved"}</span></td>
            <td>${escapeHtml(log.author || "-")}</td>
        </tr>
    `).join("");
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
