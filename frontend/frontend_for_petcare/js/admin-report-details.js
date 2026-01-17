/* =========================
   AUTH
========================= */
const token = localStorage.getItem("accessToken");
if (!token) {
  location.href = "login.html";
  throw new Error("NO_TOKEN");
}

/* =========================
   REPORT ID
========================= */
const reportId = new URLSearchParams(window.location.search).get("id");
if (!reportId) {
  location.href = "admin-reports.html";
  throw new Error("NO_REPORT_ID");
}

/* =========================
   DOM
========================= */
const animalType = document.getElementById("animalType");
const conditionEl = document.getElementById("condition");
const descriptionEl = document.getElementById("description");
const addressEl = document.getElementById("address");
const contactPhoneEl = document.getElementById("contactPhone");
const createdAtEl = document.getElementById("createdAt");
const statusBadge = document.getElementById("statusBadge");

const saveReportBtn = document.getElementById("saveReportBtn");
const saveMsg = document.getElementById("saveMsg");

const imagesGrid = document.getElementById("imagesGrid");
const noImages = document.getElementById("noImages");

const statusSelect = document.getElementById("statusSelect");
const updateStatusBtn = document.getElementById("updateStatusBtn");
const statusMsg = document.getElementById("statusMsg");

const noteInput = document.getElementById("noteInput");
const addNoteBtn = document.getElementById("addNoteBtn");
const notesList = document.getElementById("notesList");
const noNotes = document.getElementById("noNotes");

const messagesList = document.getElementById("messagesList");
const noMessages = document.getElementById("noMessages");

/* =========================
   LOAD REPORT
========================= */
async function loadReport() {
  const res = await fetch(
    `http://localhost:9002/reports/${reportId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const r = await res.json();

  animalType.value = r.animal_type;
  conditionEl.value = r.condition;
  descriptionEl.value = r.description;
  addressEl.value = r.address;
  contactPhoneEl.value = r.contact_phone || "";
  createdAtEl.textContent = new Date(r.created_at).toLocaleString();

  statusBadge.textContent = r.status;
  statusBadge.className = `status ${r.status}`;
  statusSelect.value = r.status;
}

/* =========================
   SAVE REPORT (ADMIN EDIT)
========================= */
saveReportBtn.onclick = async () => {
  saveMsg.textContent = "";

  const payload = {
    condition: conditionEl.value,
    description: descriptionEl.value,
    address: addressEl.value,
    contact_phone: contactPhoneEl.value
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
    saveMsg.textContent = "Failed to save changes";
    return;
  }

  saveMsg.textContent = "Changes saved ✔";
};

/* =========================
   IMAGES
========================= */
async function loadImages() {
  const res = await fetch(
    `http://localhost:9002/reports/${reportId}/images`
  );

  const images = await res.json();
  imagesGrid.innerHTML = "";

  if (!images.length) {
    noImages.classList.remove("hidden");
    return;
  }

  noImages.classList.add("hidden");

  images.forEach(img => {
    const div = document.createElement("div");
    div.className = "image-card";

    div.innerHTML = `
      <img src="${img.image_url}" />
      <button class="btn-danger small"
        onclick="deleteImage(${img.id})">
        Delete
      </button>
    `;

    imagesGrid.appendChild(div);
  });
}

async function deleteImage(imageId) {
  if (!confirm("Delete this image?")) return;

  await fetch(
    `http://localhost:9002/reports/images/${imageId}`,
    {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  loadImages();
}

/* =========================
   STATUS
========================= */
updateStatusBtn.onclick = async () => {
  const res = await fetch(
    `http://localhost:9002/reports/${reportId}/status`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ status: statusSelect.value })
    }
  );

  if (!res.ok) {
    statusMsg.textContent = "Status update failed";
    return;
  }

  statusMsg.textContent = "Status updated ✔";
  loadReport();
};

/* =========================
   NOTES
========================= */
addNoteBtn.onclick = async () => {
  if (!noteInput.value.trim()) return;

  await fetch(
    `http://localhost:9002/reports/${reportId}/notes`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ note: noteInput.value })
    }
  );

  noteInput.value = "";
  loadNotes();
};

async function loadNotes() {
  const res = await fetch(
    `http://localhost:9002/reports/${reportId}/notes`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const notes = await res.json();
  notesList.innerHTML = "";

  if (!notes.length) {
    noNotes.classList.remove("hidden");
    return;
  }

  noNotes.classList.add("hidden");

  notes.forEach(n => {
    const div = document.createElement("div");
    div.className = "note-item";
    div.innerHTML = `
      <p>${n.note}</p>
      <small>${new Date(n.created_at).toLocaleString()}</small>
    `;
    notesList.appendChild(div);
  });
}

/* =========================
   MESSAGES (AUTO MARK READ)
========================= */
async function loadMessages() {
  const res = await fetch(
    `http://localhost:9002/reports/${reportId}/messages`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const msgs = await res.json();
  messagesList.innerHTML = "";

  if (!msgs.length) {
    noMessages.classList.remove("hidden");
    return;
  }

  noMessages.classList.add("hidden");

  msgs.forEach(m => {
    const div = document.createElement("div");
    div.className = "message-item";
    div.innerHTML = `
      <strong>${m.sender_name}</strong>
      <p>${m.message}</p>
      <small>
        ${new Date(m.created_at).toLocaleString()}
        ${m.is_read ? " • Read" : ""}
      </small>
    `;
    messagesList.appendChild(div);
  });
}

/* =========================
   INIT
========================= */
loadReport();
loadImages();
loadNotes();
loadMessages();