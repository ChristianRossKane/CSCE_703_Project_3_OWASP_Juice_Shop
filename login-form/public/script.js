const form = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const errorMessage = document.getElementById("error-message");

function showMessage(text, isSuccess) {
  errorMessage.textContent = text;
  errorMessage.classList.toggle("success", isSuccess);
}

function validate(email, password) {
  if (!email || !password) {
    return "Email and password are required.";
  }
  if (!email.includes("@")) {
    return "Please enter a valid email address.";
  }
  if (password.length < 8) {
    return "Password must be at least 8 characters long.";
  }
  return null;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  const validationError = validate(email, password);
  if (validationError) {
    showMessage(validationError, false);
    return;
  }

  try {
    const response = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const result = await response.json();
    showMessage(result.message, result.success);
  } catch (err) {
    showMessage("Unable to reach the server. Please try again.", false);
  }
});
