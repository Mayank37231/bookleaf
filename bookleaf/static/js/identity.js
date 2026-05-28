const identityForm = document.querySelector("#identityForm");
const identifierInput = document.querySelector("#identifierInput");
const platformInput = document.querySelector("#platformInput");
const identityResult = document.querySelector("#identityResult");

identityForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    identityResult.innerHTML = '<p class="muted">Matching identity...</p>';
    const response = await fetch("/api/identify", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            identifier: identifierInput.value.trim(),
            platform: platformInput.value,
        }),
    });
    const data = await response.json();
    renderIdentity(data);
});

async function verify(linkId, action) {
    await fetch("/api/identity/verify", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({linkId, action}),
    });
    const label = action === "approved" ? "approved" : "rejected";
    document.querySelector("#verifyState").textContent = `Manually ${label}`;
}

function renderIdentity(data) {
    if (!data.author) {
        identityResult.innerHTML = '<p class="muted">No confident match found. This identifier should go to manual review.</p>';
        return;
    }

    const pct = Math.round(data.confidence * 100);
    const needsReview = data.status === "suggested";
    identityResult.innerHTML = `
        <h1>${data.author.name}</h1>
        <div class="confidence-bar"><span style="width: ${pct}%"></span></div>
        <p><span class="badge ${pct < 80 ? "warn" : ""}">${pct}% confidence</span> <span id="verifyState" class="badge">${data.status.replaceAll("_", " ")}</span></p>
        <div class="profile">
            ${row("Email", data.author.email)}
            ${row("Phone", data.author.phone)}
            ${row("Instagram", data.author.instagram)}
            ${row("Dashboard", data.author.dashboardName)}
            ${row("Book", data.author.bookTitle)}
            ${row("Package", data.author.package)}
        </div>
        ${needsReview ? `
            <div class="meta">
                <button onclick="verify(${data.linkId}, 'approved')">Approve</button>
                <button class="secondary" onclick="verify(${data.linkId}, 'rejected')">Reject</button>
            </div>
        ` : ""}
    `;
}

function row(label, value) {
    return `<div class="profile-row"><span class="muted">${label}</span><strong>${value || "Not available"}</strong></div>`;
}
