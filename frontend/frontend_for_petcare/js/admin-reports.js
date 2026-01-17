/* =========================
   AUTH
========================= */
const token = localStorage.getItem("accessToken");
if (!token) {
  location.href = "login.html";
  throw new Error("NO_TOKEN");
}

/* =========================
   STATE
========================= */
let skip = 0;
const limit = 20;
let currentStatus = "";

/* =========================
   DOM
========================= */
const reportsGrid = document.getElementById("reportsGrid");
const emptyState = document.getElementById("emptyState");
const statusFilter = document.getElementById("statusFilter");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const statsGrid = document.getElementById("statsGrid");

/* =========================
   LOAD STATS
========================= */
async function loadStats() {
  const res = await fetch(
    "http://localhost:9002/reports/stats/overview",
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!res.ok) return;

  const stats = await res.json();
  statsGrid.innerHTML = "";

  const statuses = [
    "OPEN",
    "IN_PROGRESS",
    "RESCUED",
    "TREATED",
    "TRANSFERED",
    "CLOSED",
    "REJECTED"
  ];

  statuses.forEach(s => {
    const card = document.createElement("div");
    card.className = "stat-card";
    card.innerHTML = `
      <h3>${stats[s] ?? 0}</h3>
      <p>${s.replace("_", " ")}</p>
    `;
    statsGrid.appendChild(card);
  });
}

/* =========================
   LOAD REPORTS
========================= */
async function loadReports() {
  emptyState.classList.add("hidden");
  reportsGrid.innerHTML = "";

  let url = `http://localhost:9002/reports/?skip=${skip}&limit=${limit}`;
  if (currentStatus) {
    url += `&status=${currentStatus}`;
  }

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    emptyState.classList.remove("hidden");
    return;
  }

  const reports = await res.json();

  if (!reports.length) {
    emptyState.classList.remove("hidden");
    return;
  }

  reports.forEach(r => {
    const card = document.createElement("div");
    card.className = "report-card";

    card.innerHTML = `
      <span class="status ${r.status}">${r.status}</span>
      <h3>${r.animal_type}</h3>
      <p class="muted">${r.condition}</p>
      <p>${r.address}</p>
      <small>${new Date(r.created_at).toLocaleString()}</small>
    `;

    card.onclick = () => {
      location.href = `admin-report-details.html?id=${r.id}`;
    };

    reportsGrid.appendChild(card);
  });
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
  if (skip === 0) return;
  skip -= limit;
  loadReports();
};

nextBtn.onclick = () => {
  skip += limit;
  loadReports();
};

/* =========================
   INIT
========================= */
loadStats();
loadReports();