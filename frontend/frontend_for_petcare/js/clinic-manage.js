/* =========================
   AUTH
========================= */
const accessToken = localStorage.getItem("accessToken");
if (!accessToken) location.href = "login.html";

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
  location.href = "login.html";
}

/* =========================
   CLINIC ID
========================= */
const clinicId = new URLSearchParams(location.search).get("id");
if (!clinicId) {
  alert("Invalid clinic link.");
  location.href = "my-clinics.html";
}

/* =========================
   STATE
========================= */
let originalClinic = null;
let map, marker;
let pinnedLat = null;
let pinnedLng = null;
let requirePin = false;
let profilePicUrl = null;

/* =========================
   LOAD CLINIC
========================= */
async function loadClinic() {
  const res = await fetch(
    `http://localhost:9002/clinics/${clinicId}`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );

  if (!res.ok) {
    alert("You are not allowed to view this clinic.");
    location.href = "my-clinics.html";
    return;
  }

  const c = await res.json();
  originalClinic = c;
  profilePicUrl = c.profile_pic_url || null;

  clinicName.textContent = c.name;
  clinicAddress.textContent = c.address || "-";
  descText.textContent = c.description || "-";
  phoneText.textContent = c.phone || "-";
  addressText.textContent = c.address || "-";
  latText.textContent = c.latitude ?? "-";
  lngText.textContent = c.longitude ?? "-";

  descInput.value = c.description || "";
  phoneInput.value = c.phone || "";
  addressInput.value = c.address || "";

  const pic = document.getElementById("profilePic");
  if (pic) {
    pic.src = profilePicUrl || "img/clinic-placeholder.png";
  }

  statusBadge.textContent = c.is_active ? "Active" : "Pending Approval";
  statusBadge.className = `badge ${c.is_active ? "badge-active" : "badge-pending"}`;

  if (c.owner_id) loadOwner(c.owner_id);

  loadImages();
  initMap(c.latitude, c.longitude);
}

/* =========================
   PROFILE PICTURE
========================= */
const profilePicInput = document.getElementById("profilePicInput");
const changeProfilePicBtn = document.getElementById("changeProfilePicBtn");

if (changeProfilePicBtn && profilePicInput) {
  changeProfilePicBtn.onclick = () => profilePicInput.click();

  profilePicInput.onchange = async () => {
    const file = profilePicInput.files[0];
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    const uploadRes = await fetch(
      `http://localhost:9002/images/clinics/${clinicId}`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
        body: form
      }
    );

    if (!uploadRes.ok) {
      alert("Image upload failed.");
      return;
    }

    const img = await uploadRes.json();

    const patchRes = await fetch(
      `http://localhost:9002/clinics/${clinicId}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`
        },
        body: JSON.stringify({ profile_pic_url: img.url })
      }
    );

    if (!patchRes.ok) {
      alert("Failed to update profile picture.");
      return;
    }

    profilePicUrl = img.url;
    document.getElementById("profilePic").src = img.url;
    alert("Profile picture updated.");
  };
}

/* =========================
   MAP
========================= */
function initMap(lat, lng) {
  map = L.map("map").setView(
    lat && lng ? [lat, lng] : [7.8731, 80.7718],
    lat && lng ? 15 : 7
  );

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap"
  }).addTo(map);

  if (lat && lng) placeMarker(lat, lng);

  map.on("click", e => placeMarker(e.latlng.lat, e.latlng.lng));
}

async function placeMarker(lat, lng) {
  pinnedLat = lat;
  pinnedLng = lng;

  if (marker) marker.setLatLng([lat, lng]);
  else {
    marker = L.marker([lat, lng], { draggable: true }).addTo(map);
    marker.on("dragend", async e => {
      const p = e.target.getLatLng();
      pinnedLat = p.lat;
      pinnedLng = p.lng;
      await fillAddressFromMap(p.lat, p.lng);
    });
  }

  await fillAddressFromMap(lat, lng);
}

async function fillAddressFromMap(lat, lng) {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`
    );
    if (!res.ok) return;

    const data = await res.json();
    if (!addressInput.value || requirePin) {
      addressInput.value = data.display_name || "";
      requirePin = false;
      mapHint.textContent = "Location & address updated from map";
    }
  } catch {}
}

/* =========================
   OWNER
========================= */
async function loadOwner(ownerId) {
  const res = await fetch(
    `http://localhost:9002/users/${ownerId}`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  if (!res.ok) return;

  const { data } = await res.json();
  ownerName.textContent = data.name;
  ownerEmail.textContent = data.email;
}

/* =========================
   IMAGES
========================= */
async function loadImages() {
  const res = await fetch(
    `http://localhost:9002/images/clinics/${clinicId}`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  if (!res.ok) return;

  const images = await res.json();
  imageGrid.innerHTML = images.map(img => `
    <div class="image-card">
      <img src="${img.url}">
      <button class="btn-danger" data-id="${img.id}">Delete</button>
    </div>
  `).join("");
}

/* ✅ FIXED DELETE HANDLER */
async function deleteClinicImage(imageId) {
  if (!confirm("Delete image?")) return;

  const res = await fetch(
    `http://localhost:9002/images/${imageId}`,
    {
      method: "DELETE",
      headers: { Authorization: `Bearer ${accessToken}` }
    }
  );

  if (!res.ok) {
    alert("Failed to delete image.");
    return;
  }

  loadImages();
}

/* EVENT DELEGATION (IMPORTANT) */
imageGrid.addEventListener("click", e => {
  const btn = e.target.closest("button[data-id]");
  if (!btn) return;
  deleteClinicImage(btn.dataset.id);
});

/* =========================
   ADDRESS RULE
========================= */
addressInput.oninput = () => {
  requirePin = true;
  mapHint.textContent =
    "Address edited manually. Please pin location on map to confirm.";
};

/* =========================
   SAVE CLINIC
========================= */
async function saveClinic() {
  if (requirePin) {
    alert("Please pin the location on the map to confirm address.");
    return;
  }

  const payload = {};

  if (descInput.value.trim() !== (originalClinic.description || ""))
    payload.description = descInput.value.trim();

  if (phoneInput.value.trim() !== (originalClinic.phone || ""))
    payload.phone = phoneInput.value.trim();

  if (addressInput.value.trim() !== (originalClinic.address || ""))
    payload.address = addressInput.value.trim();

  if (pinnedLat !== null && pinnedLng !== null) {
    payload.latitude = pinnedLat;
    payload.longitude = pinnedLng;
  }

  if (!Object.keys(payload).length) {
    alert("No changes detected.");
    return;
  }

  const res = await fetch(
    `http://localhost:9002/clinics/${clinicId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`
      },
      body: JSON.stringify(payload)
    }
  );

  if (!res.ok) {
    alert("Update failed.");
    return;
  }

  alert("Clinic updated successfully.");
  clinicEditForm.classList.add("hidden");
  clinicInfoView.classList.remove("hidden");
  loadClinic();
}

/* =========================
   EVENTS
========================= */
editClinicBtn.onclick = () => {
  clinicInfoView.classList.add("hidden");
  clinicEditForm.classList.remove("hidden");
};

cancelEdit.onclick = () => {
  clinicEditForm.classList.add("hidden");
  clinicInfoView.classList.remove("hidden");
};

saveClinicBtn.onclick = saveClinic;
uploadImageBtn.onclick = () => imageInput.click();

imageInput.onchange = async () => {
  const form = new FormData();
  form.append("file", imageInput.files[0]);

  await fetch(
    `http://localhost:9002/images/clinics/${clinicId}`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}` },
      body: form
    }
  );

  imageInput.value = "";
  loadImages();
};

manageAppointmentsBtn.onclick = () =>
  location.href = `appointments.html?clinic_id=${clinicId}`;

toggleDelete.onclick = () =>
  deleteBox.classList.toggle("hidden");

deleteConfirm.oninput = e =>
  deleteBtn.disabled = e.target.value !== "DELETE CLINIC";

deleteBtn.onclick = async () => {
  await fetch(
    `http://localhost:9002/clinics/${clinicId}`,
    {
      method: "DELETE",
      headers: { Authorization: `Bearer ${accessToken}` }
    }
  );
  alert("Clinic deleted.");
  location.href = "my-clinics.html";
};

/* =========================
   INIT
========================= */
loadClinic();