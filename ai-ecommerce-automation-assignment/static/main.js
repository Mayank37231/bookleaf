const output = document.querySelector("#output");
const form = document.querySelector("#ticketForm");
const loadDemo = document.querySelector("#loadDemo");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderResult(result) {
  const actions = result.recommended_actions.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  const policies = result.retrieved_policy_titles.map((item) => `<span class="pill">${escapeHtml(item)}</span>`).join("");
  const risks = result.risk_flags.length
    ? result.risk_flags.map((item) => `<span class="pill warn">${escapeHtml(item.replaceAll("_", " "))}</span>`).join("")
    : '<span class="pill">No risk flags</span>';
  return `
    <article class="result-card">
      <div class="meta-row">
        <span class="pill">${escapeHtml(result.ticket_id)}</span>
        <span class="pill">${escapeHtml(result.intent)}</span>
        <span class="pill">Confidence ${Math.round(result.confidence * 100)}%</span>
        <span class="pill">${escapeHtml(result.order_id || "No order resolved")}</span>
        ${result.escalated ? '<span class="pill warn">Human review</span>' : '<span class="pill">Auto-resolve</span>'}
      </div>
      <p>${escapeHtml(result.response)}</p>
      <strong>Model route</strong>
      <div class="meta-row small-gap">
        <span class="pill route">${escapeHtml(result.model_route)}</span>
        ${risks}
      </div>
      <strong>Recommended actions</strong>
      <ul>${actions}</ul>
      <div class="meta-row small-gap">${policies}</div>
    </article>
  `;
}

function renderResults(results) {
  output.innerHTML = results.map(renderResult).join("");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const response = await fetch("/api/analyze", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      customer_email: document.querySelector("#email").value,
      message: document.querySelector("#message").value
    })
  });
  renderResults([await response.json()]);
});

loadDemo.addEventListener("click", async () => {
  const response = await fetch("/api/demo");
  const payload = await response.json();
  renderResults(payload.results);
});

loadDemo.click();
