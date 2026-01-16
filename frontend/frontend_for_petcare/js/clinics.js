/* =========================
   DOM
========================= */
const grid = document.getElementById("clinicGrid");
const searchInput = document.getElementById("searchInput");

/* =========================
   STATE
========================= */
let clinics = [];
let searchTimer = null;

/* =========================
   LOAD CLINICS (REAL BACKEND)
========================= */
async function loadClinics(query = "") {
  try {
    const url = new URL("http://localhost:9002/clinics/");
    url.searchParams.set("limit", 50);

    if (query) {
      url.searchParams.set("name", query);
    }

    const res = await fetch(url.toString());

    if (!res.ok) {
      grid.innerHTML = "<p>Failed to load clinics.</p>";
      return;
    }

    clinics = await res.json();
    renderClinics(clinics);

  } catch (err) {
    console.error(err);
    grid.innerHTML = "<p>Error loading clinics.</p>";
  }
}

/* =========================
   RENDER CLINICS
========================= */
function renderClinics(list) {
  grid.innerHTML = "";

  if (!list.length) {
    grid.innerHTML = "<p>No clinics found.</p>";
    return;
  }

  list.forEach(c => {
    const card = document.createElement("div");
    card.className = "clinic-card";

    card.innerHTML = `
      <h3>${c.name}</h3>
      <p class="location">
        📍 ${c.address || "Address not available"}
      </p>

      <button class="btn-primary"
        onclick="viewClinic(${c.id})">
        View Clinic
      </button>
    `;

    grid.appendChild(card);
  });
}

/* =========================
   VIEW CLINIC
========================= */
function viewClinic(id) {
  window.location.href = `clinic-public.html?id=${id}`;
}

/* =========================
   SEARCH (DEBOUNCED)
========================= */
searchInput.addEventListener("input", e => {
  const value = e.target.value.trim();

  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    loadClinics(value);
  }, 300);
});

/* =========================
   INIT
========================= */
loadClinics();