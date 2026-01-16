/* =========================
   CLINIC ID
========================= */
const clinicId = new URLSearchParams(window.location.search).get("id");
if (!clinicId) location.href = "clinics.html";

/* =========================
   AUTH
========================= */
const token = localStorage.getItem("accessToken");

/* =========================
   DOM
========================= */
const slotsBtn = document.getElementById("slotsBtn");
const slotsSection = document.getElementById("slotsSection");
const slotDate = document.getElementById("slotDate");
const slotsGrid = document.getElementById("slotsGrid");
const noSlots = document.getElementById("noSlots");

const bookingBox = document.getElementById("bookingBox");
const bookingInfo = document.getElementById("bookingInfo");
const bookingMessage = document.getElementById("bookingMessage");
const confirmBookingBtn = document.getElementById("confirmBookingBtn");

const authBox = document.getElementById("authActions");

/* =========================
   STATE
========================= */
let map = null;
let selectedSlot = null;
let slotsVisible = false;

/* =========================
   LOAD CLINIC
========================= */
async function loadClinic() {
  const res = await fetch(`http://localhost:9002/clinics/${clinicId}`);
  if (!res.ok) location.href = "clinics.html";

  const clinic = await res.json();
  fillClinic(clinic);
  loadGallery();

  // ✅ SAFE map init
  waitForLeaflet(() => {
    initMap(clinic.latitude, clinic.longitude);
  });
}

/* =========================
   FILL DATA
========================= */
function fillClinic(c) {
  clinicName.textContent = c.name;
  clinicDesc.textContent = c.description || "No description provided.";
  clinicAddress.textContent = `📍 ${c.address || "-"}`;
  clinicPhone.textContent = `📞 ${c.phone || "-"}`;

  detailName.textContent = c.name;
  detailAddress.textContent = c.address || "-";
  detailPhone.textContent = c.phone || "-";
  detailCreated.textContent =
    new Date(c.created_at).toLocaleDateString();

  if (c.profile_pic_url) {
    document.querySelector(".clinic-hero").style.backgroundImage =
      `linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.45)), url(${c.profile_pic_url})`;
    document.querySelector(".clinic-hero").style.color = "#fff";
  }
}

/* =========================
   LOAD GALLERY
========================= */
async function loadGallery() {
  try {
    const res = await fetch(`http://localhost:9002/clinics/${clinicId}/gallery`);
    
    if (!res.ok) {
      document.getElementById("noImages").classList.remove("hidden");
      return;
    }

    const images = await res.json();
    renderGallery(images);
  } catch (err) {
    console.error("Gallery load error:", err);
    document.getElementById("noImages").classList.remove("hidden");
  }
}

/* =========================
   RENDER GALLERY
========================= */
function renderGallery(images) {
  const galleryGrid = document.getElementById("galleryGrid");
  const noImages = document.getElementById("noImages");
  
  galleryGrid.innerHTML = "";
  noImages.classList.toggle("hidden", images.length > 0);

  images.forEach(img => {
    const imgCard = document.createElement("div");
    imgCard.className = "gallery-item";
    imgCard.innerHTML = `<img src="${img.image_url}" alt="Clinic image" />`;
    galleryGrid.appendChild(imgCard);
  });
}

/* =========================
   LEAFLET SAFE LOADER
========================= */
function waitForLeaflet(cb) {
  if (window.L) {
    cb();
  } else {
    setTimeout(() => waitForLeaflet(cb), 50);
  }
}

/* =========================
   MAP (FINAL FIX)
========================= */
function initMap(lat, lng) {
  if (!lat || !lng) return;

  if (map) {
    map.remove();
  }

  map = L.map("map", {
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false
  }).setView([lat, lng], 15);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap"
  }).addTo(map);

  L.marker([lat, lng]).addTo(map);

  // ✅ REQUIRED for hidden containers / layout shifts
  setTimeout(() => map.invalidateSize(), 200);
}

/* =========================
   SLOTS BUTTON
========================= */
slotsBtn.onclick = () => {
  if (!slotsVisible) {
    slotsSection.classList.remove("hidden");
    slotsVisible = true;
    loadSlots();
  }

  slotsSection.scrollIntoView({ behavior: "smooth" });
};

/* =========================
   SLOT DATE
========================= */
const today = new Date().toISOString().split("T")[0];
slotDate.min = today;
slotDate.value = today;
slotDate.onchange = loadSlots;

/* =========================
   LOAD SLOTS
========================= */
async function loadSlots() {
  const res = await fetch(
    `http://localhost:9002/appointments/slots/${clinicId}/available?date=${slotDate.value}`,
    token ? { headers: { Authorization: `Bearer ${token}` } } : {}
  );

  const slots = await res.json();
  renderSlots(slots);
}

/* =========================
   RENDER SLOTS
========================= */
function renderSlots(slots) {
  slotsGrid.innerHTML = "";
  noSlots.classList.toggle("hidden", slots.length > 0);

  slots.forEach(s => {
    const card = document.createElement("div");
    card.className = "slot-card" + (s.is_booked ? " booked" : "");

    const start = new Date(s.start_time).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });
    const end = new Date(s.end_time).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });

    card.innerHTML = `
      <strong>${start} – ${end}</strong><br/>
      ${s.is_booked ? "Booked" : "<button class='btn-primary'>Book</button>"}
    `;

    if (!s.is_booked) {
      card.querySelector("button").onclick = () => openBooking(s);
    }

    slotsGrid.appendChild(card);
  });
}

/* =========================
   BOOKING
========================= */
function openBooking(slot) {
  if (!token) {
    bookingMessage.textContent = "Please sign in to book appointments.";
    return;
  }

  selectedSlot = slot;
  bookingInfo.textContent =
    `Confirm booking from ${new Date(slot.start_time).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}
     to ${new Date(slot.end_time).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}`;

  bookingBox.classList.remove("hidden");
}

function closeBookingBox() {
  bookingBox.classList.add("hidden");
  selectedSlot = null;
}

confirmBookingBtn.onclick = async () => {
  if (!selectedSlot) return;

  const res = await fetch(
    "http://localhost:9002/appointments/bookings",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        clinic_id: Number(clinicId),
        start_time: selectedSlot.start_time,
        end_time: selectedSlot.end_time
      })
    }
  );

  const data = await res.json();

  if (!res.ok) {
    bookingMessage.textContent = data.detail || "Booking failed.";
    return;
  }

  bookingMessage.textContent = "Appointment booked successfully ✔";
  closeBookingBox();
  loadSlots();
};

/* =========================
   HEADER AUTH
========================= */
authBox.innerHTML = token
  ? `<a href="my-appointments.html" class="btn-link">My Appointments</a>`
  : `<a href="login.html" class="btn-link">Sign In</a>`;

/* =========================
   INIT
========================= */
document.addEventListener("DOMContentLoaded", loadClinic);