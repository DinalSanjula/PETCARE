/* =========================
   CONFIG
========================= */
const LIMIT = 20;
let skip = 0;
let currentStatus = "";

/* =========================
   DOM
========================= */
const reportsGrid = document.getElementById("reportsGrid");
const emptyState = document.getElementById("emptyState");
const statusFilter = document.getElementById("statusFilter");

const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

/* =========================
   LOAD REPORTS
========================= */
async function loadReports() {
  reportsGrid.innerHTML = "";
  emptyState.classList.add("hidden");

  let url = `http://localhost:9002/reports/?skip=${skip}&limit=${LIMIT}`;

  if (currentStatus) {
    url += `&status=${currentStatus}`;
  }

  const res = await fetch(url);
  if (!res.ok) {
    emptyState.classList.remove("hidden");
    return;
  }

  const reports = await res.json();

  if (!Array.isArray(reports) || reports.length === 0) {
    emptyState.classList.remove("hidden");
    return;
  }

  renderReports(reports);

  // pagination logic
  prevBtn.disabled = skip === 0;
  nextBtn.disabled = reports.length < LIMIT;
}

/* =========================
   RENDER
========================= */
function renderReports(list) {
  reportsGrid.innerHTML = list.map(r => {
    const date = new Date(r.created_at).toLocaleDateString();

    const shortDesc = r.description
      ? r.description.slice(0, 90) + (r.description.length > 90 ? "…" : "")
      : "No description";

    return `
      <div class="report-card" onclick="openReport(${r.id})">
        <span class="status-badge ${r.status}">${r.status}</span>

        <h3>${r.animal_type} · ${r.condition}</h3>

        <p class="location">📍 ${r.address}</p>

        <p class="desc">${shortDesc}</p>

        <div class="meta">🕒 ${date}</div>
      </div>
    `;
  }).join("");
}

/* =========================
   NAVIGATION
========================= */
function openReport(id) {
  window.location.href = `report-details.html?id=${id}`;
}

/* =========================
   FILTER
========================= */
statusFilter.onchange = () => {
  currentStatus = statusFilter.value;
  skip = 0;
  loadReports();
};

/* =========================
   PAGINATION
========================= */
prevBtn.onclick = () => {
  if (skip >= LIMIT) {
    skip -= LIMIT;
    loadReports();
  }
};

nextBtn.onclick = () => {
  skip += LIMIT;
  loadReports();
};

/* =========================
   AUTH NAV
========================= */
const authBox = document.getElementById("authActions");
const token = localStorage.getItem("accessToken");

authBox.innerHTML = token
  ? `
    <a href="my-reports.html" class="btn-link">My Reports</a>
  `
  : `
    <a href="login.html" class="btn-link">Sign In</a>
  `;

/* =========================
   INIT
========================= */
loadReports();