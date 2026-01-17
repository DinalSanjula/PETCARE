/* =========================
   AUTH CHECK
========================= */
const accessToken = localStorage.getItem("accessToken");

if (!accessToken) {
  window.location.href = "login.html";
}

/* =========================
   JWT
========================= */
function decodeJWT(token) {
  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch {
    return null;
  }
}

const decoded = decodeJWT(accessToken);

if (!decoded?.user_id) {
  localStorage.clear();
  window.location.href = "login.html";
}

const userId = decoded.user_id;

/* =========================
   DOM
========================= */
const clinicsGrid = document.getElementById("clinicsGrid");
const emptyState = document.getElementById("emptyState");

/* =========================
   LOAD CLINICS
========================= */
async function loadMyClinics() {
  try {
    const res = await fetch(
      `http://localhost:9002/clinics/?owner_id=${userId}`,
      {
        headers: { Authorization: `Bearer ${accessToken}` }
      }
    );

    if (!res.ok) throw new Error();

    const clinics = await res.json();

    clinicsGrid.innerHTML = "";
    emptyState.classList.add("hidden");

    if (!Array.isArray(clinics) || clinics.length === 0) {
      emptyState.classList.remove("hidden");
      return;
    }

    renderClinics(clinics);

  } catch (err) {
    console.error(err);
    clinicsGrid.innerHTML =
      `<p class="error-text">Failed to load clinics.</p>`;
  }
}

/* =========================
   RENDER
========================= */
function renderClinics(clinics) {
  clinicsGrid.innerHTML = clinics.map(c => {
    const img =
      c.profile_pic_url
        ? c.profile_pic_url
        : "https://via.placeholder.com/600x400?text=Clinic+Image";

    return `
      <div class="clinic-card">

        <img src="${img}" alt="${c.name}" />

        <div class="clinic-body">

          <span class="badge ${c.is_active ? "badge-active" : "badge-pending"}">
            ${c.is_active ? "Active" : "Pending Approval"}
          </span>

          <h3>${c.name}</h3>

          <p>${c.description || "No description provided."}</p>

          <p class="meta">📍 ${c.address || "Address not set"}</p>
          <p class="meta">📞 ${c.phone || "-"}</p>

          <div class="card-actions">
            <button class="btn-outline"
              onclick="viewClinic(${c.id})">
              View
            </button>

            <button class="btn-primary"
              onclick="manageClinic(${c.id})">
              Manage
            </button>

            <button class="btn-primary full"
              onclick="manageAppointments(${c.id})">
              Appointments
            </button>
          </div>

        </div>
      </div>
    `;
  }).join("");
}

/* =========================
   NAVIGATION
========================= */
function viewClinic(id) {
  window.location.href = `clinic-public.html?id=${id}`;
}

function manageClinic(id) {
  window.location.href = `clinic-manage.html?id=${id}`;
}

function manageAppointments(id) {
  window.location.href = `clinic-slots.html?clinic_id=${id}`;
}

function goToCreateClinic() {
  window.location.href = "clinic-create.html";
}

/* =========================
   INIT
========================= */
loadMyClinics();