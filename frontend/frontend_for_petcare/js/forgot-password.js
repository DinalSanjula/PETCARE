const form = document.getElementById("forgotForm");
const emailError = document.getElementById("emailError");

form.addEventListener("submit", (e) => {
  e.preventDefault();

  emailError.textContent = "";

  const email = document.getElementById("email").value.trim();

  if (!email) {
    emailError.textContent = "Please enter your email address.";
    return;
  }

  // TODO: Backend integration
  // fetch("/api/auth/forgot-password", {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({ email })
  // })

  alert(
    "If this email is registered, a password reset link will be sent."
  );

  form.reset();
});