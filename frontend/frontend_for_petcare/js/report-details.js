/* =========================
   AUTH
========================= */
const token = localStorage.getItem("accessToken");

/* =========================
   REPORT ID
========================= */
const reportId = new URLSearchParams(window.location.search).get("id");
if (!reportId) {
  location.href = "reports.html";
}

/* =========================
   DOM
========================= */
const authBox = document.getElementById("authBox");

const animalType = document.getElementById("animalType");
const conditionEl = document.getElementById("condition");
const descriptionEl = document.getElementById("description");
const addressEl = document.getElementById("address");
const contactWrapper = document.getElementById("contactWrapper");
const contactPhone = document.getElementById("contactPhone");
const createdAt = document.getElementById("createdAt");
const statusBadge = document.getElementById("statusBadge");

const imagesGrid = document.getElementById("imagesGrid");
const noImages = document.getElementById("noImages");

const messageSection = document.getElementById("messageSection");
const messageInput = document.getElementById("messageInput");
const sendMessageBtn = document.getElementById("sendMessageBtn");
const messageStatus = document.getElementById("messageStatus");

/* =========================
   HEADER AUTH
========================= */
authBox.innerHTML = token
  ? `<a href="logout.html" class="btn-link">Logout</a>`
  : `<a href="login.html" class="btn-link">Sign In</a>`;

/* =========================
   LOAD REPORT
========================= */
async function loadReport() {
  const res = await fetch(
    `http://localhost:9002/reports/${reportId}`,
    token ? { headers: { Authorization: `Bearer ${token}` } } : {}
  );

  if (!res.ok) {
    location.href = "reports.html";
    return;
  }

  const r = await res.json();

  animalType.textContent = r.animal_type;
  conditionEl.textContent = r.condition;
  descriptionEl.textContent = r.description;
  addressEl.textContent = r.address;

  if (r.contact_phone) {
    contactWrapper.classList.remove("hidden");
    contactPhone.textContent = r.contact_phone;
  }

  statusBadge.textContent = r.status;
  statusBadge.classList.add(r.status);

  createdAt.textContent =
    "Reported on " + new Date(r.created_at).toLocaleString();

  // Message section only if logged in
  if (token) {
    messageSection.classList.remove("hidden");
  }
}

/* =========================
   LOAD IMAGES
========================= */
async function loadImages() {
  const res = await fetch(
    `http://localhost:9002/reports/${reportId}/images`
  );

  if (!res.ok) return;

  const images = await res.json();
  imagesGrid.innerHTML = "";

  if (!images.length) {
    noImages.classList.remove("hidden");
    return;
  }

  images.forEach(img => {
    const el = document.createElement("img");
    el.src = img.image_url;
    imagesGrid.appendChild(el);
  });
}

/* =========================
   SEND MESSAGE
========================= */
sendMessageBtn.onclick = async () => {
  const msg = messageInput.value.trim();
  if (!msg) return;

  const res = await fetch(
    `http://localhost:9002/reports/${reportId}/messages`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ message: msg })
    }
  );

  if (!res.ok) {
    messageStatus.textContent = "Failed to send message.";
    return;
  }

  messageInput.value = "";
  messageStatus.textContent = "Message sent successfully ✔";
};

/* =========================
   INIT
========================= */
loadReport();
loadImages();