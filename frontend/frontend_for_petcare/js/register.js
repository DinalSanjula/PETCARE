/* =========================
   ROLE HANDLING
   ========================= */
const params = new URLSearchParams(window.location.search);
const role = params.get("role");

const allowedRoles = ["owner", "clinic", "welfare"];
if (!allowedRoles.includes(role)) {
  window.location.href = "login.html";
}

/* =========================
   UI TEXT BASED ON ROLE
   ========================= */
const title = document.getElementById("registerTitle");
const subtitle = document.getElementById("registerSubtitle");

if (role === "owner") {
  title.textContent = "Register as Pet Owner";
  subtitle.textContent =
    "Create an account to manage pets, appointments, and reports.";
} else if (role === "clinic") {
  title.textContent = "Register as Clinic";
  subtitle.textContent =
    "Join PetCare as a veterinary clinic.";
} else if (role === "welfare") {
  title.textContent = "Register as Welfare Partner";
  subtitle.textContent =
    "Contribute to animal welfare and reporting.";
}

/* =========================
   FORM + VALIDATION
   ========================= */
const form = document.getElementById("registerForm");
const passwordError = document.getElementById("passwordError");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  passwordError.textContent = "";

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const confirmPassword =
    document.getElementById("confirmPassword").value;

  if (password.length < 6) {
    passwordError.textContent =
      "Password must be at least 6 characters long.";
    return;
  }

  if (password !== confirmPassword) {
    passwordError.textContent = "Passwords do not match.";
    return;
  }

  try {
    const res = await fetch("http://localhost:9002/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name,
        email,
        password,
        role
      })
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      passwordError.textContent =
        data.message || "Registration failed.";
      return;
    }

    // Backend already returns tokens
    localStorage.setItem("accessToken", data.data.access_token);
    localStorage.setItem("refreshToken", data.data.refresh_token);

    // Go directly to user dashboard
    window.location.href = "user.html";

  } catch (err) {
    console.error(err);
    passwordError.textContent =
      "Server error. Please try again.";
  }
});

/* Clear error when user types again */
document
  .getElementById("confirmPassword")
  .addEventListener("input", () => {
    passwordError.textContent = "";
  });