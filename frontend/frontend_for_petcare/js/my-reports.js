/* =========================
   AUTH
========================= */
const token = localStorage.getItem("accessToken");
if (!token) {
  location.href = "login.html";
}

/* =========================
   DOM
========================= */
const reportsGrid = document.getElementById("reportsGrid");
const emptyState = document.getElementById("emptyState");

/* =========================
   LOAD MY REPORTS
========================= */
async function loadMyReports() {
  try {
    const res = await fetch(
      "http://localhost:9002/reports/my",
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    if (!res.ok) throw new Error();

    const reports = await res.json();

    if (!Array.isArray(reports) || reports.length === 0) {
      emptyState.classList.remove("hidden");
      reportsGrid.innerHTML = "";
      return;
    }

    renderReports(reports);

  } catch (err) {
    console.error(err);
    reportsGrid.innerHTML =
      `<p class="muted">Failed to load your reports.</p>`;
  }
}

/* =========================
   RENDER
========================= */
function renderReports(list) {
  reportsGrid.innerHTML = list.map(r => {
    const date = new Date(r.created_at);

    return `
      <div class="report-card" onclick="openReport(${r.id})">

        <span class="status ${r.status.replace(" ", "_")}">
          ${r.status}
        </span>

        <h3>${r.animal_type}</h3>

        <p class="condition">
          ${r.condition}
        </p>

        <p class="desc">
          ${r.description || "No description"}
        </p>

        <div class="meta">
          <span>📍 ${r.address || "-"}</span>
          <span>🗓 ${date.toLocaleDateString()}</span>
        </div>

      </div>
    `;
  }).join("");
}

/* =========================
   NAVIGATION
========================= */
function openReport(id) {
  location.href = `report-edit.html?id=${id}`;
}

/* =========================
   INIT
========================= */
loadMyReports();