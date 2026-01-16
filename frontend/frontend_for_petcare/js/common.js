// Handle header auth link (Sign In / My Profile)
document.addEventListener("DOMContentLoaded", () => {
  const authLink = document.getElementById("authLink");
  const token = localStorage.getItem("accessToken");

  if (!authLink) return;

  if (token) {
    authLink.textContent = "My Profile";
    authLink.href = "user.html";
  } else {
    authLink.textContent = "Sign In";
    authLink.href = "login.html";
  }
});

// Navigation guard for protected pages
function goTo(page) {
  const token = localStorage.getItem("accessToken");

  if (!token) {
    localStorage.setItem("redirectAfterLogin", page);
    window.location.href = "login.html";
  } else {
    window.location.href = page;
  }
}

function goToRegister(role) {
  window.location.href = `register.html?role=${role}`;
}