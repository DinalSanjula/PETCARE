/* =========================
   AUTH CHECK
   ========================= */
const accessToken = localStorage.getItem("accessToken");
const refreshToken = localStorage.getItem("refreshToken");

if (!accessToken) {
  window.location.href = "login.html";
}

/* =========================
   JWT DECODE
   ========================= */
function decodeJWT(token) {
  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch {
    return null;
  }
}

const decoded = decodeJWT(accessToken);

if (!decoded || !decoded.user_id) {
  localStorage.clear();
  window.location.href = "login.html";
}

const userId = decoded.user_id;

/* =========================
   FETCH USER PROFILE
   ========================= */
async function loadUserProfile() {
  try {
    const res = await fetch(`http://localhost:9002/users/${userId}`, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      }
    });

    if (!res.ok) throw new Error("Failed to fetch user");

    const result = await res.json();
    const user = result.data;

    // Fill profile
    document.getElementById("userName").textContent = user.name;
    document.getElementById("userEmail").textContent = user.email;
    document.getElementById("userRole").textContent = user.role;
    document.getElementById("userCreated").textContent =
      new Date(user.created_at).toLocaleDateString();

    buildDashboard(user.role);
  } catch (err) {
    console.error(err);
    localStorage.clear();
    window.location.href = "login.html";
  }
}

/* =========================
   DASHBOARD BUILDER
   ========================= */
function buildDashboard(role) {
  const dashboardCard = document.getElementById("dashboardCard");

  /* ---------- OWNER ---------- */
  if (role === "owner") {
    dashboardCard.innerHTML = `
      <h2>Dashboard</h2>
      <p class="main-desc">
        Manage your pets, book appointments, and track medical records.
      </p>

      <div class="dashboard-actions-grid">
        <div class="dashboard-box">
          <h4>Register Pet</h4>
          <p>Add a new pet to your account.</p>
          <button class="btn-primary">Register Pet</button>
        </div>

        <div class="dashboard-box">
          <h4>View Pets</h4>
          <p>View and manage your pets.</p>
          <button class="btn-outline">View Pets</button>
        </div>
      </div>
    `;
  }

  /* ---------- CLINIC ---------- */
  if (role === "clinic") {
    dashboardCard.innerHTML = `
      <h2>Dashboard</h2>
      <p class="main-desc">
        Manage your clinics and appointments.
      </p>

      <div class="dashboard-actions-grid" id="clinicActions">
        <p class="muted">Loading clinics...</p>
      </div>
    `;

    loadClinicDashboard();
  }

  /* ---------- WELFARE ---------- */
  if (role === "welfare") {
    dashboardCard.innerHTML = `
      <h2>Dashboard</h2>
      <p class="main-desc">
        Create and manage animal welfare reports.
      </p>

      <div class="dashboard-actions-grid">
        <div class="dashboard-box">
          <h4>Create Report</h4>
          <p>Report welfare incidents.</p>
          <button class="btn-primary">Create Report</button>
        </div>

        <div class="dashboard-box">
          <h4>View Reports</h4>
          <p>Manage your reports.</p>
          <button class="btn-outline">View Reports</button>
        </div>
      </div>
    `;
  }

  /* ---------- ADMIN ---------- */
  if (role === "admin") {
    dashboardCard.innerHTML = `
      <h2>Dashboard</h2>
      <p class="main-desc">
        Manage users and system operations.
      </p>

      <div class="dashboard-actions-grid">
        <div class="dashboard-box">
          <h4>Admin Panel</h4>
          <p>Administrative controls.</p>
          <button class="btn-primary">Admin Panel</button>
        </div>

        <div class="dashboard-box">
          <h4>System Stats</h4>
          <p>Platform health and statistics.</p>
          <button class="btn-outline">View Stats</button>
        </div>
      </div>
    `;
  }
}

/* =========================
   CLINIC DASHBOARD (REAL)
   ========================= */
async function loadClinicDashboard() {
  const container = document.getElementById("clinicActions");

  try {
    const res = await fetch(
      `http://localhost:9002/clinics?owner_id=${userId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      }
    );

    if (!res.ok) throw new Error("Failed to load clinics");

    // ✅ BACKEND RETURNS ARRAY DIRECTLY
    const clinics = await res.json();

    if (!Array.isArray(clinics) || clinics.length === 0) {
      container.innerHTML = `
        <div class="dashboard-box">
          <h4>Register Clinic</h4>
          <p>You haven’t registered a clinic yet.</p>
          <button class="btn-primary"
            onclick="location.href='clinic-create.html'">
            Register Clinic
          </button>
        </div>
      `;
      return;
    }

    // ✅ HAS CLINICS
    container.innerHTML = `
      <div class="dashboard-box">
        <h4>My Clinics</h4>
        <p>You manage ${clinics.length} clinic(s).</p>

        ${clinics.map(c => `
          <div class="muted" style="margin:6px 0">
            • ${c.name} (${c.is_active ? "Active" : "Pending approval"})
          </div>
        `).join("")}

        <button class="btn-primary"
          style="margin-top:10px"
          onclick="location.href='my-clinics.html'">
          View My Clinics
        </button>
      </div>
    `;
  } catch (err) {
    console.error(err);
    container.innerHTML =
      `<p class="error-text">Failed to load clinic data.</p>`;
  }
}

/* =========================
   CHANGE PASSWORD
   ========================= */
document.getElementById("togglePw").onclick = () => {
  document.getElementById("pwBox").classList.toggle("hidden");
};

document.querySelector("#pwBox .btn-primary").onclick = async () => {
  const newPassword = document.getElementById("newPassword").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const error = document.getElementById("pwError");

  error.textContent = "";

  if (newPassword.length < 6) {
    error.textContent = "Password must be at least 6 characters.";
    return;
  }

  if (newPassword !== confirmPassword) {
    error.textContent = "Passwords do not match.";
    return;
  }

  try {
    const res = await fetch(
      `http://localhost:9002/users/${userId}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`
        },
        body: JSON.stringify({ password: newPassword })
      }
    );

    if (!res.ok) throw new Error();

    alert("Password updated successfully");
    document.getElementById("pwBox").classList.add("hidden");
  } catch {
    error.textContent = "Failed to update password.";
  }
};

/* =========================
   LOGOUT (BACKEND + FRONTEND)
   ========================= */
document.getElementById("logoutBtn").onclick = async () => {
  try {
    await fetch(
      `http://localhost:9002/auth/logout?refresh_token=${refreshToken}`,
      { method: "POST" }
    );
  } catch {}

  localStorage.clear();
  window.location.href = "index.html";
};

/* =========================
   INIT
   ========================= */
loadUserProfile();