/* =========================
   AUTH
========================= */
const token = localStorage.getItem("accessToken");
if (!token) location.href = "login.html";

/* =========================
   DOM
========================= */
const grid = document.getElementById("appointmentsGrid");
const emptyState = document.getElementById("emptyState");

const cancelModal = document.getElementById("cancelModal");
const confirmCancelBtn = document.getElementById("confirmCancelBtn");

let cancelBookingId = null;

/* =========================
   LOAD APPOINTMENTS
========================= */
async function loadAppointments() {
  const res = await fetch(
    "http://localhost:9002/appointments/my",
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const data = await res.json();

  if (!res.ok || !Array.isArray(data)) {
    grid.innerHTML = "<p class='muted'>Failed to load appointments.</p>";
    return;
  }

  if (data.length === 0) {
    emptyState.classList.remove("hidden");
    return;
  }

  renderAppointments(data);
}

/* =========================
   RENDER
========================= */
function renderAppointments(list) {
  grid.innerHTML = list.map(a => {
    const start = new Date(a.start_time);
    const end = new Date(a.end_time);

    const time =
      `${start.toLocaleDateString()} · ` +
      `${start.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})} - ` +
      `${end.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`;

    const actions =
      a.status === "CONFIRMED"
        ? `
          <button class="btn-outline"
            onclick="reschedule(${a.booking_id}, ${a.clinic_id})">
            Reschedule
          </button>
          <button class="btn-danger" onclick="openCancelModal(${a.booking_id})">
            Cancel
          </button>
        `
        : "";

    return `
      <div class="appointment-card">
        <span class="status ${a.status}">${a.status}</span>
        <h3>${a.clinic_name}</h3>
        <div class="appointment-meta">${time}</div>
        <div class="card-actions">${actions}</div>
      </div>
    `;
  }).join("");
}

/* =========================
   CANCEL FLOW
========================= */
function openCancelModal(id) {
  cancelBookingId = id;
  cancelModal.classList.remove("hidden");
}

function closeCancelModal() {
  cancelBookingId = null;
  cancelModal.classList.add("hidden");
}

confirmCancelBtn.onclick = async () => {
  if (!cancelBookingId) return;

  await fetch(
    `http://localhost:9002/appointments/bookings/${cancelBookingId}/cancel`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  closeCancelModal();
  loadAppointments();
};

/* =========================
   RESCHEDULE FLOW
========================= */
const rescheduleModal = document.getElementById("rescheduleModal");
const rescheduleDate = document.getElementById("rescheduleDate");
const rescheduleSlots = document.getElementById("rescheduleSlots");
const rescheduleMsg = document.getElementById("rescheduleMsg");

let rescheduleBookingId = null;
let rescheduleClinicId = null;

/* OPEN MODAL */
function reschedule(bookingId, clinicId) {
  rescheduleBookingId = bookingId;
  rescheduleClinicId = clinicId;

  rescheduleModal.classList.remove("hidden");
  rescheduleMsg.textContent = "";
  rescheduleSlots.innerHTML = "";

  const today = new Date().toISOString().split("T")[0];
  rescheduleDate.min = today;
  rescheduleDate.value = today;

  loadRescheduleSlots();
}

/* CLOSE MODAL */
function closeRescheduleModal() {
  rescheduleModal.classList.add("hidden");
  rescheduleBookingId = null;
  rescheduleClinicId = null;
}

/* DATE CHANGE */
rescheduleDate.onchange = loadRescheduleSlots;

/* LOAD AVAILABLE SLOTS */
async function loadRescheduleSlots() {
  if (!rescheduleClinicId) return;

  const res = await fetch(
    `http://localhost:9002/appointments/slots/${rescheduleClinicId}/available?date=${rescheduleDate.value}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const slots = await res.json();
  renderRescheduleSlots(slots);
}

/* RENDER SLOTS */
function renderRescheduleSlots(slots) {
  rescheduleSlots.innerHTML = "";

  if (!Array.isArray(slots) || slots.length === 0) {
    rescheduleMsg.textContent = "No available slots.";
    return;
  }

  slots.forEach(s => {
    if (s.is_booked) return;

    const btn = document.createElement("button");
    btn.className = "btn-primary";

    const start = new Date(s.start_time).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });
    const end = new Date(s.end_time).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });

    btn.textContent = `${start} - ${end}`;

    btn.onclick = () => confirmReschedule(s);
    rescheduleSlots.appendChild(btn);
  });
}

/* CONFIRM RESCHEDULE */
async function confirmReschedule(slot) {
  const res = await fetch(
    `http://localhost:9002/appointments/bookings/${rescheduleBookingId}/reschedule`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        start_time: slot.start_time,
        end_time: slot.end_time
      })
    }
  );

  if (!res.ok) {
    rescheduleMsg.textContent = "Failed to reschedule appointment.";
    return;
  }

  closeRescheduleModal();
  loadAppointments();
}

/* =========================
   INIT
========================= */
loadAppointments();