/* =========================
   AUTH
========================= */
const token = localStorage.getItem("accessToken");

if (!token) {
  window.location.replace("login.html");
  throw new Error("NO_TOKEN");
}

/* =========================
   DOM
========================= */
const form = document.getElementById("reportForm");
const errorText = document.getElementById("formError");

const animalType = document.getElementById("animalType");
const condition = document.getElementById("condition");
const description = document.getElementById("description");
const address = document.getElementById("address");
const contactPhone = document.getElementById("contactPhone");
const imageInput = document.getElementById("image");

/* =========================
   SUBMIT
========================= */
function isValidPhone(phone) {
  if (!phone) return true; // optional field

  const localPattern = /^0\d{9}$/;        // 0771234567
  const intlPattern = /^\+94\d{9}$/;      // +94771234567

  return localPattern.test(phone) || intlPattern.test(phone);
}

form.onsubmit = async (e) => {
  e.preventDefault();
  errorText.textContent = "";

  if (
    !animalType.value ||
    !condition.value ||
    !description.value ||
    !address.value
  ) {
    errorText.textContent = "Please fill all required fields.";
    return;
  }
  // 📞 Phone validation
    if (!isValidPhone(contactPhone.value.trim())) {
        errorText.textContent =
        "Invalid phone number. Use 0771234567 or +94771234567 format.";
    return;
    }

  if (imageInput.files[0] && imageInput.files[0].size > 5 * 1024 * 1024) {
    errorText.textContent = "Image size must be under 5MB.";
    return;
  }

  const formData = new FormData();
  formData.append("animal_type", animalType.value);
  formData.append("condition", condition.value);
  formData.append("description", description.value);
  formData.append("address", address.value);

  if (contactPhone.value) {
    formData.append("contact_phone", contactPhone.value);
  }

  if (imageInput.files[0]) {
    formData.append("image", imageInput.files[0]);
  }

  try {
    const res = await fetch("http://localhost:9002/reports/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    });

    const data = await res.json();

    if (!res.ok) {
      errorText.textContent = data.detail || "Failed to create report.";
      return;
    }

    // ✅ Success → redirect
    window.location.href = "my-reports.html";

  } catch (err) {
    console.error(err);
    errorText.textContent = "Network error. Please try again.";
  }
};