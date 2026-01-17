/* =========================
   AUTH
========================= */
const token = localStorage.getItem("accessToken");
if (!token) {
  window.location.replace("login.html");
  throw new Error("NO_TOKEN");
}

/* =========================
   CLINIC ID (HARD LOCK)
========================= */
const params = new URLSearchParams(window.location.search);
const clinicId = params.get("clinic_id");

if (!clinicId) {
  console.error("clinic_id missing in URL");
  window.location.replace("my-clinics.html");
  throw new Error("NO_CLINIC_ID");
}

/* =========================
   DOM
========================= */
const slotsGrid = document.getElementById("slotsGrid");
const bookingsGrid = document.getElementById("bookingsGrid");
const slotError = document.getElementById("slotError");

const rescheduleModal = document.getElementById("rescheduleModal");
const rescheduleDate = document.getElementById("rescheduleDate");
const rescheduleSlots = document.getElementById("rescheduleSlots");

const totalBookings = document.getElementById("totalBookings");
const confirmedBookings = document.getElementById("confirmedBookings");
const cancelledBookings = document.getElementById("cancelledBookings");
const upcomingBookings = document.getElementById("upcomingBookings");

let rescheduleBookingId = null;

/* =========================
   STATS
========================= */
async function loadStats() {
  const res = await fetch(
    "http://localhost:9002/appointments/stats/clinic",
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!res.ok) return;

  const s = await res.json();
  totalBookings.textContent = s.total_bookings ?? 0;
  confirmedBookings.textContent = s.confirmed ?? 0;
  cancelledBookings.textContent = s.cancelled ?? 0;
  upcomingBookings.textContent = s.upcoming ?? 0;
}

/* =========================
   CREATE SLOT
========================= */
createSlotBtn.onclick = async () => {
  slotError.textContent = "";

  if (!slotDate.value || !startTime.value || !endTime.value) {
    slotError.textContent = "Date, start time and end time are required";
    return;
  }

  // derive day of week from date
  const dayOfWeek = new Date(slotDate.value)
    .toLocaleDateString("en-US", { weekday: "long" })
    .toUpperCase();

  const payload = {
    clinic_id: Number(clinicId),
    day_of_week: dayOfWeek,          // ✅ REQUIRED
    start_time: startTime.value,     // "16:30"
    end_time: endTime.value          // "16:40"
  };

  const res = await fetch("http://localhost:9002/appointments/slots", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  if (!res.ok) {
    slotError.textContent = data.detail || "Failed to create slot";
    return;
  }

  startTime.value = "";
  endTime.value = "";

  loadSlots();
};
/* =========================
   LOAD ALL SLOTS (CLINIC)
========================= */
async function loadSlots() {
  if (!clinicId) return;

  const res = await fetch(
    `http://localhost:9002/appointments/slots/clinic/${clinicId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!res.ok) return;

  const slots = await res.json();
  slotsGrid.innerHTML = "";

  slots.forEach(s => {
    const start = new Date(s.start_time);
    const end = new Date(s.end_time);

    const card = document.createElement("div");
    card.className = `slot-card ${!s.is_active ? "disabled" : ""}`;

    card.innerHTML = `
      <strong>${start.toLocaleDateString()}</strong>

      <div class="slot-time">
        ${start.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
        -
        ${end.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
      </div>

      ${s.has_bookings ? `<span class="badge booked">Booked</span>` : ""}

      <div class="card-actions">
        <button class="btn-outline"
          ${s.has_bookings ? "disabled" : ""}
          onclick="toggleSlot(${s.id}, ${s.is_active})">
          ${s.is_active ? "Disable" : "Enable"}
        </button>
      </div>
    `;

    slotsGrid.appendChild(card);
  });
}

/* =========================
   ENABLE / DISABLE SLOT
========================= */
async function toggleSlot(id, active) {
  const res = await fetch(
    `http://localhost:9002/appointments/slots/${id}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ is_active: !active })
    }
  );

  if (!res.ok) {
    const d = await res.json();
    alert(d.detail || "Cannot update slot");
    return;
  }

  loadSlots();
}

/* =========================
   LOAD BOOKINGS
========================= */
async function loadBookings() {
  if (!clinicId) return;

  const res = await fetch(
    `http://localhost:9002/appointments/clinic/${clinicId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!res.ok) return;

  const list = await res.json();
  bookingsGrid.innerHTML = "";

  list.forEach(b => {
    const start = new Date(b.start_time);
    const end = new Date(b.end_time);
    const disabled = b.status !== "CONFIRMED";

    const card = document.createElement("div");
    card.className = "booking-card";

    card.innerHTML = `
      <h4>${b.owner_name}</h4>
      <p class="muted">${b.owner_email}</p>

      <p>
        ${start.toLocaleDateString()}
        ${start.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
        -
        ${end.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
      </p>

      <span class="status ${b.status}">${b.status}</span>

      <div class="card-actions">
        <button class="btn-outline"
          ${disabled ? "disabled" : ""}
          onclick="openReschedule(${b.booking_id})">
          Reschedule
        </button>

        <button class="btn-danger"
          ${disabled ? "disabled" : ""}
          onclick="cancelBooking(${b.booking_id})">
          Cancel
        </button>
      </div>
    `;

    bookingsGrid.appendChild(card);
  });
}

/* =========================
   CANCEL BOOKING
========================= */
async function cancelBooking(id) {
  if (!confirm("Cancel this booking?")) return;

  await fetch(
    `http://localhost:9002/appointments/bookings/${id}/cancel`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  loadBookings();
  loadStats();
}

/* =========================
   RESCHEDULE
========================= */
function openReschedule(id) {
  rescheduleBookingId = id;
  rescheduleModal.classList.remove("hidden");
}

function closeReschedule() {
  rescheduleBookingId = null;
  rescheduleModal.classList.add("hidden");
}

rescheduleDate.onchange = async () => {
  const res = await fetch(
    `http://localhost:9002/appointments/slots/${clinicId}/available?date=${rescheduleDate.value}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!res.ok) return;

  const slots = await res.json();
  rescheduleSlots.innerHTML = "";

  slots.filter(s => !s.is_booked).forEach(s => {
    const btn = document.createElement("button");
    btn.className = "btn-primary";
    btn.textContent =
      `${new Date(s.start_time).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
       - ${new Date(s.end_time).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`;

    btn.onclick = async () => {
      await fetch(
        `http://localhost:9002/appointments/bookings/${rescheduleBookingId}/reschedule`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            start_time: s.start_time,
            end_time: s.end_time
          })
        }
      );

      closeReschedule();
      loadBookings();
      loadStats();
    };

    rescheduleSlots.appendChild(btn);
  });
};

/* =========================
   INIT
========================= */
loadStats();
loadSlots();
loadBookings();