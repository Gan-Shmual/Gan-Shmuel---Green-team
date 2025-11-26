// -----------------------------
// Helpers
// -----------------------------

// Convert agorot → shekels
function agorotToShekels(amount) {
  if (!amount || isNaN(amount)) return "0.00";
  return (amount / 100).toFixed(2);
}

// -----------------------------
// Notification System
// -----------------------------
function showNotification(title, message, type = "success") {
  const notification = document.getElementById("notification");
  const notificationIcon = document.getElementById("notification-icon");
  const notificationTitle = document.getElementById("notification-title");
  const notificationMessage = document.getElementById("notification-message");

  notificationTitle.textContent = title;
  notificationMessage.textContent = message;

  // Icon colors
  const types = {
      success: "fas fa-check-circle text-green-500",
      error: "fas fa-exclamation-circle text-red-500",
      warning: "fas fa-exclamation-triangle text-yellow-500",
      info: "fas fa-info-circle text-blue-500",
  };

  notificationIcon.className = types[type] || types.info;

  notification.classList.remove("hidden");

  // Auto-hide after 5 seconds
  setTimeout(() => notification.classList.add("hidden"), 5000);
}

// Close button
document.addEventListener("DOMContentLoaded", () => {
  const closeBtn = document.getElementById("notification-close");
  if (closeBtn) {
      closeBtn.addEventListener("click", () => {
          document.getElementById("notification").classList.add("hidden");
      });
  }
});

// -----------------------------
// Validation
// -----------------------------
function validateRequired(fieldId, errorMessage) {
  const field = document.getElementById(fieldId);
  const value = field.value.trim();

  if (!value) {
      showFieldError(fieldId, errorMessage);
      return false;
  }

  clearFieldError(fieldId);
  return true;
}

function showFieldError(fieldId, message) {
  const field = document.getElementById(fieldId);
  field.classList.add("error");

  let errorElement = field.parentNode.querySelector(".error-message");
  if (!errorElement) {
      errorElement = document.createElement("p");
      errorElement.className = "error-message";
      field.parentNode.appendChild(errorElement);
  }

  errorElement.textContent = message;
}

function clearFieldError(fieldId) {
  const field = document.getElementById(fieldId);
  field.classList.remove("error");

  const errorElement = field.parentNode.querySelector(".error-message");
  if (errorElement) errorElement.remove();
}

// -----------------------------
// API Helper (fetch wrapper)
// -----------------------------
function apiRequest(url, options = {}) {
  const base = {
      headers: { "Content-Type": "application/json" },
  };

  const opts = { ...base, ...options };

  return fetch(url, opts).then(async (res) => {
      const text = await res.text();
      let data;

      try { data = JSON.parse(text); }
      catch { data = text; }

      if (!res.ok) throw new Error(data.error || text || "Request failed");

      return data;
  });
}

// -----------------------------
// Date Helpers
// -----------------------------
function formatDateTime(date) {
  const pad = (n) => String(n).padStart(2, "0");

  return (
      date.getFullYear() +
      pad(date.getMonth() + 1) +
      pad(date.getDate()) +
      pad(date.getHours()) +
      pad(date.getMinutes()) +
      pad(date.getSeconds())
  );
}

function formatDateTimeDisplay(str) {
  if (str.length !== 14) return str;

  const yyyy = str.slice(0, 4);
  const mm = str.slice(4, 6);
  const dd = str.slice(6, 8);
  const hh = str.slice(8, 10);
  const mi = str.slice(10, 12);
  const ss = str.slice(12, 14);

  return new Date(`${yyyy}-${mm}-${dd}T${hh}:${mi}:${ss}`).toLocaleString();
}

// -----------------------------
// Loading Spinner
// -----------------------------
function showLoading(elementId) {
  const el = document.getElementById(elementId);
  el.innerHTML = `
    <div class="flex justify-center items-center p-4">
        <div class="spinner"></div>
    </div>`;
}

// Expose globally
window.agorotToShekels = agorotToShekels;
window.showNotification = showNotification;
window.validateRequired = validateRequired;
window.showFieldError = showFieldError;
window.clearFieldError = clearFieldError;
window.apiRequest = apiRequest;
window.formatDateTime = formatDateTime;
window.formatDateTimeDisplay = formatDateTimeDisplay;
window.showLoading = showLoading;
