/* =========================
   SIGNUP TOGGLE (UNCHANGED)
   ========================= */
const signupBtn = document.getElementById("showSignup");
const signupSection = document.getElementById("signupSection");

if (signupBtn && signupSection) {
  signupBtn.addEventListener("click", () => {
    signupSection.classList.remove("hidden");
    signupSection.scrollIntoView({ behavior: "smooth" });
  });
}

function goToRegister(role) {
  window.location.href = `register.html?role=${role}`;
}

/* =========================
   LOGIN (REAL BACKEND)
   ========================= */
const loginForm = document.getElementById("loginForm");
const loginError =
  document.getElementById("loginError") ||
  (() => {
    const el = document.createElement("small");
    el.className = "error-text";
    loginForm.appendChild(el);
    return el;
  })();

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginError.textContent = "";

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    const res = await fetch("http://localhost:9002/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      loginError.textContent =
        data.detail || "Incorrect email or password.";
      return;
    }

    // Save tokens
    localStorage.setItem("accessToken", data.data.access_token);
    localStorage.setItem("refreshToken", data.data.refresh_token);

    // Redirect handling
    const redirect = localStorage.getItem("redirectAfterLogin");
    if (redirect) {
      localStorage.removeItem("redirectAfterLogin");
      window.location.href = redirect;
    } else {
      window.location.href = "user.html";
    }

  } catch (err) {
    console.error(err);
    loginError.textContent = "Server error. Please try again.";
  }
});