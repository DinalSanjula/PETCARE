/* =========================
   AUTH
========================= */
const token = localStorage.getItem("accessToken");
if (!token) location.href = "login.html";

/* =========================
   DOM ELEMENTS
========================= */
const form = document.getElementById("clinicForm");
const errorBox = document.getElementById("formError");
const areaSelect = document.getElementById("area");
const mapHint = document.getElementById("mapHint");

const nameInput = document.getElementById("name");
const descriptionInput = document.getElementById("description");
const phoneInput = document.getElementById("phone");
const addressInput = document.getElementById("address");

/* =========================
   MAP STATE
========================= */
let map, marker;
let selectedLat = null;
let selectedLng = null;

/* =========================
   DISTRICTS (Sri Lanka) – UI ONLY
========================= */
const DISTRICTS = {
  Colombo: [6.9271, 79.8612],
  Gampaha: [7.0873, 79.9990],
  Kalutara: [6.5836, 79.9590],
  Kandy: [7.2906, 80.6337],
  Matale: [7.4690, 80.6217],
  NuwaraEliya: [6.9497, 80.7891],
  Galle: [6.0535, 80.2210],
  Matara: [5.9549, 80.5540],
  Hambantota: [6.1241, 81.1185],
  Jaffna: [9.6615, 80.0255],
  Kilinochchi: [9.3803, 80.3769],
  Mannar: [8.9810, 79.9044],
  Mullaitivu: [9.2671, 80.8142],
  Vavuniya: [8.7514, 80.4971],
  Kurunegala: [7.4863, 80.3647],
  Puttalam: [8.0408, 79.8394],
  Anuradhapura: [8.3114, 80.4037],
  Polonnaruwa: [7.9403, 81.0188],
  Badulla: [6.9934, 81.0550],
  Monaragala: [6.8714, 81.3507],
  Ratnapura: [6.7056, 80.3847],
  Kegalle: [7.2513, 80.3464],
  Trincomalee: [8.5874, 81.2152],
  Batticaloa: [7.7170, 81.7000],
  Ampara: [7.3018, 81.6747],
};

/* =========================
   POPULATE DISTRICT DROPDOWN
========================= */
function populateDistricts() {
  Object.keys(DISTRICTS).forEach(district => {
    const opt = document.createElement("option");
    opt.value = district;
    opt.textContent = district;
    areaSelect.appendChild(opt);
  });
}

/* =========================
   INIT MAP
========================= */
function initMap() {
  map = L.map("map").setView([7.8731, 80.7718], 7);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap",
  }).addTo(map);

  map.on("click", e => {
    selectedLat = e.latlng.lat;
    selectedLng = e.latlng.lng;

    if (marker) {
      marker.setLatLng(e.latlng);
    } else {
      marker = L.marker(e.latlng).addTo(map);
    }

    mapHint.textContent = "Location pinned ✔";
  });

  // Fix hidden container render issue
  setTimeout(() => map.invalidateSize(), 200);
}

/* =========================
   DISTRICT → MAP ZOOM (UI ONLY)
========================= */
areaSelect.addEventListener("change", () => {
  const district = areaSelect.value;
  if (!DISTRICTS[district]) return;

  const [lat, lng] = DISTRICTS[district];
  map.setView([lat, lng], 11);
});

/* =========================
   SUBMIT FORM
========================= */
form.addEventListener("submit", async e => {
  e.preventDefault();
  errorBox.textContent = "";

  if (!nameInput.value.trim()) {
    errorBox.textContent = "Clinic name is required.";
    return;
  }

  if (!selectedLat || !selectedLng) {
    errorBox.textContent = "Please pin clinic location on the map.";
    return;
  }

  const payload = {
    name: nameInput.value.trim(),
    description: descriptionInput.value.trim() || null,
    phone: phoneInput.value.trim() || null,
    address: addressInput.value.trim() || null,
    latitude: selectedLat,
    longitude: selectedLng,
  };

  try {
    const res = await fetch("http://localhost:9002/clinics", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    const clinic = await res.json();

    if (!res.ok) {
      if (Array.isArray(clinic.detail)) {
        errorBox.textContent = clinic.detail.map(d => d.msg).join(", ");
      } else {
        errorBox.textContent = clinic.detail || "Failed to create clinic.";
      }
      return;
    }

    alert("Clinic registered successfully. Pending admin approval.");
    location.href = "my-clinics.html";

  } catch (err) {
    console.error(err);
    errorBox.textContent = "Server error. Please try again.";
  }
});

/* =========================
   INIT
========================= */
document.addEventListener("DOMContentLoaded", () => {
  populateDistricts();
  initMap();
});