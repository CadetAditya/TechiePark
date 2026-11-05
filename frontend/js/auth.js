/**
 * Techie Park - Authentication Module (Vanilla JS)
 */

// API Configuration
const API_BASE_URL = window.location.origin.includes(":8000") 
  ? window.location.origin 
  : "http://127.0.0.1:8000";

// DOM Elements
const tabLogin = document.getElementById("tabLogin");
const tabSignup = document.getElementById("tabSignup");
const formLogin = document.getElementById("formLogin");
const formSignup = document.getElementById("formSignup");
const alertBox = document.getElementById("alertBox");
const alertMessage = document.getElementById("alertMessage");
const navAuthToggle = document.getElementById("navAuthToggle");
const authCard = document.getElementById("authCard");

// Toggle Buttons for Show/Hide Password
const toggleLoginPassword = document.getElementById("toggleLoginPassword");
const loginPasswordInput = document.getElementById("loginPassword");
const toggleSignupPassword = document.getElementById("toggleSignupPassword");
const signupPasswordInput = document.getElementById("signupPassword");

// Google Buttons
const googleAuthBtn = document.getElementById("googleAuthBtn");

// -------------------------------------------------------------
// UI Utilities: Alerts & Feedback
// -------------------------------------------------------------
function showAlert(message, type = "error") {
  alertBox.className = `alert-box visible alert-${type}`;
  alertMessage.textContent = message;
  alertBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function clearAlert() {
  alertBox.className = "alert-box";
  alertMessage.textContent = "";
}

function setButtonLoading(buttonId, spinnerId, isLoading, textDefault) {
  const btn = document.getElementById(buttonId);
  const spinner = document.getElementById(spinnerId);
  const btnText = btn.querySelector(".btn-text");

  btn.disabled = isLoading;
  if (isLoading) {
    spinner.style.display = "inline-block";
    btnText.textContent = "Processing...";
  } else {
    spinner.style.display = "none";
    btnText.textContent = textDefault;
  }
}

// -------------------------------------------------------------
// Tab Switching (Login <-> Sign Up)
// -------------------------------------------------------------
function switchToLogin() {
  clearAlert();
  tabLogin.classList.add("active");
  tabSignup.classList.remove("active");
  formLogin.style.display = "block";
  formSignup.style.display = "none";
}

function switchToSignup() {
  clearAlert();
  tabSignup.classList.add("active");
  tabLogin.classList.remove("active");
  formSignup.style.display = "block";
  formLogin.style.display = "none";
}

tabLogin.addEventListener("click", switchToLogin);
tabSignup.addEventListener("click", switchToSignup);

if (navAuthToggle) {
  navAuthToggle.addEventListener("click", () => {
    authCard.scrollIntoView({ behavior: "smooth" });
    if (formLogin.style.display === "none") {
      loginPasswordInput.focus();
    } else {
      document.getElementById("loginEmail").focus();
    }
  });
}

// -------------------------------------------------------------
// Show / Hide Password Toggles
// -------------------------------------------------------------
function setupPasswordToggle(button, input) {
  if (!button || !input) return;
  button.addEventListener("click", () => {
    const isPassword = input.type === "password";
    input.type = isPassword ? "text" : "password";
    button.textContent = isPassword ? "🙈" : "👁️";
  });
}

setupPasswordToggle(toggleLoginPassword, loginPasswordInput);
setupPasswordToggle(toggleSignupPassword, signupPasswordInput);

// -------------------------------------------------------------
// Handle Sign Up Submission
// -------------------------------------------------------------
formSignup.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearAlert();

  const fullName = document.getElementById("signupFullName").value.trim();
  const email = document.getElementById("signupEmail").value.trim();
  const password = document.getElementById("signupPassword").value;
  const confirmPassword = document.getElementById("signupConfirmPassword").value;

  // Frontend Validation
  if (fullName.length < 2) {
    showAlert("Please enter your full name (minimum 2 characters).", "error");
    return;
  }
  if (!email.includes("@") || !email.includes(".")) {
    showAlert("Please provide a valid email address.", "error");
    return;
  }
  if (password.length < 6) {
    showAlert("Password must be at least 6 characters long.", "error");
    return;
  }
  if (password !== confirmPassword) {
    showAlert("Passwords do not match! Please check again.", "error");
    return;
  }

  setButtonLoading("btnSignupSubmit", "signupSpinner", true, "Create Account");

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: fullName,
        email: email,
        password: password
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Registration failed. Please try again.");
    }

    // Store JWT token & user information
    localStorage.setItem("techiepark_token", data.access_token);
    localStorage.setItem("techiepark_user", JSON.stringify(data.user));

    showAlert("🎉 Account created successfully! Redirecting to setup your profile...", "success");

    setTimeout(() => {
      // Redirect to personal info / profile page
      window.location.href = "profile.html";
    }, 1200);

  } catch (error) {
    showAlert(error.message, "error");
  } finally {
    setButtonLoading("btnSignupSubmit", "signupSpinner", false, "Create Account");
  }
});

// -------------------------------------------------------------
// Handle Login Submission
// -------------------------------------------------------------
formLogin.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearAlert();

  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;

  if (!email || !password) {
    showAlert("Please fill in both email and password.", "error");
    return;
  }

  setButtonLoading("btnLoginSubmit", "loginSpinner", true, "Sign In");

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        password: password
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Login failed. Check your credentials.");
    }

    // Store JWT token & user information
    localStorage.setItem("techiepark_token", data.access_token);
    localStorage.setItem("techiepark_user", JSON.stringify(data.user));

    showAlert("✓ Welcome back! Logging you in...", "success");

    setTimeout(() => {
      if (data.is_profile_completed) {
        window.location.href = "dashboard.html";
      } else {
        window.location.href = "profile.html";
      }
    }, 1000);

  } catch (error) {
    showAlert(error.message, "error");
  } finally {
    setButtonLoading("btnLoginSubmit", "loginSpinner", false, "Sign In");
  }
});

// -------------------------------------------------------------
// Google Sign-In Integration
// -------------------------------------------------------------
googleAuthBtn.addEventListener("click", async () => {
  clearAlert();
  
  // Prompt user for their Google email or use one-click mock for testing
  const enteredEmail = prompt("Enter your Google Account email (or click OK for default test student):", "student.developer@gmail.com");
  if (!enteredEmail) return;

  showAlert("Signing in with Google...", "success");

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: enteredEmail,
        name: enteredEmail.split("@")[0].replace(".", " ").toUpperCase(),
        google_id: "google_" + btoa(enteredEmail).substring(0, 16),
        avatar_url: `https://api.dicebear.com/7.x/identicon/svg?seed=${enteredEmail}`
      })
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Google authentication failed.");
    }

    localStorage.setItem("techiepark_token", data.access_token);
    localStorage.setItem("techiepark_user", JSON.stringify(data.user));

    showAlert("✓ Google Sign-in successful! Redirecting...", "success");

    setTimeout(() => {
      if (data.is_profile_completed) {
        window.location.href = "dashboard.html";
      } else {
        window.location.href = "profile.html";
      }
    }, 1000);

  } catch (error) {
    showAlert(error.message, "error");
  }
});

// Check if already authenticated
window.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("techiepark_token");
  const user = localStorage.getItem("techiepark_user");
  if (token && user) {
    try {
      const parsedUser = JSON.parse(user);
      const greeting = document.createElement("div");
      greeting.style.cssText = "font-size:0.85rem; color:#8B949E; margin-bottom:1rem; text-align:center;";
      greeting.innerHTML = `Signed in as <strong style="color:#58A6FF;">${parsedUser.full_name}</strong> (<a href="#" id="btnLogout" style="color:#F85149; text-decoration:none;">Log out</a>)`;
      authCard.insertBefore(greeting, authCard.firstChild);
      
      document.getElementById("btnLogout").addEventListener("click", (e) => {
        e.preventDefault();
        localStorage.removeItem("techiepark_token");
        localStorage.removeItem("techiepark_user");
        window.location.reload();
      });
    } catch (e) {}
  }
});

