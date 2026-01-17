const token = localStorage.getItem("accessToken");
if (!token) location.href = "login.html";

const reportId = new URLSearchParams(window.location.search).get("id");
if (!reportId) location.href = "my-reports.html";

const animalType = document.getElementById("animalType");
const condition = document.getElementById("condition");
const description = document.getElementById("description");
const address = document.getElementById("address");
const contactPhone = document.getElementById("contactPhone");
const formError = document.getElementById("formError");
const imagesGrid = document.getElementById("imagesGrid");
const imageInput = document.getElementById("imageInput");
const updateBtn = document.getElementById("updateBtn");
const statusBadge = document.getElementById("statusBadge");

let reportStatus = "";
let imageCount = 0;

/* =========================
   LOAD REPORT
========================= */
async function loadReport() {
  const res = await fetch(
    `http://localhost:9002/reports/${reportId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!res.ok) return location.href = "my-reports.html";

  const r = await res.json();

  animalType.value = r.animal_type;
  condition.value = r.condition;
  description.value = r.description;
  address.value = r.address;
  contactPhone.value = r.contact_phone || "";

  reportStatus = r.status;
  statusBadge.textContent = r.status;
  statusBadge.classList.add(`status-${r.status}`);

  if (["CLOSED", "REJECTED"].includes(r.status)) {
    disableEditing();
  }

  loadImages();
}

/* =========================
   DISABLE EDIT
========================= */
function disableEditing() {
  condition.disabled = true;
  description.disabled = true;
  address.disabled = true;
  contactPhone.disabled = true;
  imageInput.disabled = true;
  updateBtn.disabled = true;
}

/* =========================
   UPDATE REPORT
========================= */
updateBtn.onclick = async () => {
  formError.textContent = "";

  if (contactPhone.value &&
      !/^\+?[0-9]{9,15}$/.test(contactPhone.value)) {
    formError.textContent = "Invalid phone number format";
    return;
  }

  const payload = {
    condition: condition.value,
    description: description.value,
    address: address.value,
    contact_phone: contactPhone.value || null
  };

  const res = await fetch(
    `http://localhost:9002/reports/${reportId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    }
  );

  if (!res.ok) {
    const d = await res.json();
    formError.textContent = d.detail || "Update failed";
    return;
  }

  alert("Report updated successfully");
};

/* =========================
   IMAGES
========================= */
async function loadImages() {
  const res = await fetch(
    `http://localhost:9002/reports/${reportId}/images`
  );

  const images = await res.json();
  imageCount = images.length;
  imagesGrid.innerHTML = "";

  images.forEach(img => {
    const div = document.createElement("div");
    div.className = "image-card";

    div.innerHTML = `
      <img src="${img.image_url}" />
      <button class="btn-danger btn-sm"
        onclick="deleteImage(${img.id})">✕</button>
    `;

    imagesGrid.appendChild(div);
  });
}

/* =========================
   UPLOAD IMAGE (MAX 3)
========================= */
imageInput.onchange = async () => {
  if (imageCount >= 3) {
    alert("Maximum 3 images allowed");
    imageInput.value = "";
    return;
  }

  const file = imageInput.files[0];
  if (!file) return;

  const fd = new FormData();
  fd.append("file", file);

  const res = await fetch(
    `http://localhost:9002/reports/${reportId}/images`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: fd
    }
  );

  if (!res.ok) {
    alert("Failed to upload image");
    return;
  }

  imageInput.value = "";
  loadImages();
};

/* =========================
   DELETE IMAGE
========================= */
async function deleteImage(id) {
  if (!confirm("Delete this image?")) return;

  await fetch(
    `http://localhost:9002/reports/images/${id}`,
    {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  loadImages();
}

/* =========================
   DELETE REPORT
========================= */
async function deleteReport() {
  if (!confirm("Delete this report permanently?")) return;

  await fetch(
    `http://localhost:9002/reports/${reportId}`,
    {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  location.href = "my-reports.html";
}

function goBack() {
  history.back();
}

/* INIT */
loadReport();