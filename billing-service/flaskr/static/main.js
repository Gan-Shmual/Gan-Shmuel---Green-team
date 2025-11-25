// Notification system
function showNotification(title, message, type = "success") {
    const notification = document.getElementById("notification");
    const notificationIcon = document.getElementById("notification-icon");
    const notificationTitle = document.getElementById("notification-title");
    const notificationMessage = document.getElementById("notification-message");
  
    notificationTitle.textContent = title;
    notificationMessage.textContent = message;
  
    // Set icon and color based on type
    if (type === "success") {
      notificationIcon.className = "fas fa-check-circle text-green-500";
    } else if (type === "error") {
      notificationIcon.className = "fas fa-exclamation-circle text-red-500";
    } else if (type === "warning") {
      notificationIcon.className = "fas fa-exclamation-triangle text-yellow-500";
    } else if (type === "info") {
      notificationIcon.className = "fas fa-info-circle text-blue-500";
    }
  
    notification.classList.remove("hidden");
  
    // Auto-hide after 5 seconds
    setTimeout(() => {
      notification.classList.add("hidden");
    }, 5000);
  }
  
  // Close notification when clicking the close button
  document.addEventListener("DOMContentLoaded", function () {
    const notificationClose = document.getElementById("notification-close");
    if (notificationClose) {
      notificationClose.addEventListener("click", function () {
        document.getElementById("notification").classList.add("hidden");
      });
    }
  });
  
  // Form validation helpers
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
  
    // Find or create error message element
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
    if (errorElement) {
      errorElement.remove();
    }
  }
  
  // API request helpers
  function apiRequest(url, options = {}) {
    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
      },
    };
  
    const mergedOptions = { ...defaultOptions, ...options };
  
    return fetch(url, mergedOptions).then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error(text || "Network response was not ok");
        });
      }
  
      // Check if response is JSON
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return response.json();
      }
  
      return response.text();
    });
  }
  
  // Date formatting helpers
  function formatDateTime(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
  
    return `${year}${month}${day}${hours}${minutes}${seconds}`;
  }
  
  function formatDateTimeDisplay(dateString) {
    // Parse yyyymmddhhmmss format
    if (dateString.length === 14) {
      const year = dateString.substring(0, 4);
      const month = dateString.substring(4, 6);
      const day = dateString.substring(6, 8);
      const hours = dateString.substring(8, 10);
      const minutes = dateString.substring(10, 12);
      const seconds = dateString.substring(12, 14);
  
      const date = new Date(
        `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
      );
      return date.toLocaleString();
    }
  
    return dateString;
  }
  
  // Loading indicator
  function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML =
      '<div class="flex justify-center items-center p-4"><div class="spinner"></div></div>';
  }
  
  // Export functions for use in other scripts
  window.showNotification = showNotification;
  window.validateRequired = validateRequired;
  window.showFieldError = showFieldError;
  window.clearFieldError = clearFieldError;
  window.apiRequest = apiRequest;
  window.formatDateTime = formatDateTime;
  window.formatDateTimeDisplay = formatDateTimeDisplay;
  window.showLoading = showLoading;// Notification system
  function showNotification(title, message, type = "success") {
    const notification = document.getElementById("notification");
    const notificationIcon = document.getElementById("notification-icon");
    const notificationTitle = document.getElementById("notification-title");
    const notificationMessage = document.getElementById("notification-message");
  
    notificationTitle.textContent = title;
    notificationMessage.textContent = message;
  
    // Set icon and color based on type
    if (type === "success") {
      notificationIcon.className = "fas fa-check-circle text-green-500";
    } else if (type === "error") {
      notificationIcon.className = "fas fa-exclamation-circle text-red-500";
    } else if (type === "warning") {
      notificationIcon.className = "fas fa-exclamation-triangle text-yellow-500";
    } else if (type === "info") {
      notificationIcon.className = "fas fa-info-circle text-blue-500";
    }
  
    notification.classList.remove("hidden");
  
    // Auto-hide after 5 seconds
    setTimeout(() => {
      notification.classList.add("hidden");
    }, 5000);
  }
  
  // Close notification when clicking the close button
  document.addEventListener("DOMContentLoaded", function () {
    const notificationClose = document.getElementById("notification-close");
    if (notificationClose) {
      notificationClose.addEventListener("click", function () {
        document.getElementById("notification").classList.add("hidden");
      });
    }
  });
  
  // Form validation helpers
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
  
    // Find or create error message element
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
    if (errorElement) {
      errorElement.remove();
    }
  }
  
  // API request helpers
  function apiRequest(url, options = {}) {
    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
      },
    };
  
    const mergedOptions = { ...defaultOptions, ...options };
  
    return fetch(url, mergedOptions).then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error(text || "Network response was not ok");
        });
      }
  
      // Check if response is JSON
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return response.json();
      }
  
      return response.text();
    });
  }
  
  // Date formatting helpers
  function formatDateTime(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
  
    return `${year}${month}${day}${hours}${minutes}${seconds}`;
  }
  
  function formatDateTimeDisplay(dateString) {
    // Parse yyyymmddhhmmss format
    if (dateString.length === 14) {
      const year = dateString.substring(0, 4);
      const month = dateString.substring(4, 6);
      const day = dateString.substring(6, 8);
      const hours = dateString.substring(8, 10);
      const minutes = dateString.substring(10, 12);
      const seconds = dateString.substring(12, 14);
  
      const date = new Date(
        `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
      );
      return date.toLocaleString();
    }
  
    return dateString;
  }
  
  // Loading indicator
  function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML =
      '<div class="flex justify-center items-center p-4"><div class="spinner"></div></div>';
  }
  
  // Export functions for use in other scripts
  window.showNotification = showNotification;
  window.validateRequired = validateRequired;
  window.showFieldError = showFieldError;
  window.clearFieldError = clearFieldError;
  window.apiRequest = apiRequest;
  window.formatDateTime = formatDateTime;
  window.formatDateTimeDisplay = formatDateTimeDisplay;
  window.showLoading = showLoading;// Notification system
  function showNotification(title, message, type = "success") {
    const notification = document.getElementById("notification");
    const notificationIcon = document.getElementById("notification-icon");
    const notificationTitle = document.getElementById("notification-title");
    const notificationMessage = document.getElementById("notification-message");
  
    notificationTitle.textContent = title;
    notificationMessage.textContent = message;
  
    // Set icon and color based on type
    if (type === "success") {
      notificationIcon.className = "fas fa-check-circle text-green-500";
    } else if (type === "error") {
      notificationIcon.className = "fas fa-exclamation-circle text-red-500";
    } else if (type === "warning") {
      notificationIcon.className = "fas fa-exclamation-triangle text-yellow-500";
    } else if (type === "info") {
      notificationIcon.className = "fas fa-info-circle text-blue-500";
    }
  
    notification.classList.remove("hidden");
  
    // Auto-hide after 5 seconds
    setTimeout(() => {
      notification.classList.add("hidden");
    }, 5000);
  }
  
  // Close notification when clicking the close button
  document.addEventListener("DOMContentLoaded", function () {
    const notificationClose = document.getElementById("notification-close");
    if (notificationClose) {
      notificationClose.addEventListener("click", function () {
        document.getElementById("notification").classList.add("hidden");
      });
    }
  });
  
  // Form validation helpers
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
  
    // Find or create error message element
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
    if (errorElement) {
      errorElement.remove();
    }
  }
  
  // API request helpers
  function apiRequest(url, options = {}) {
    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
      },
    };
  
    const mergedOptions = { ...defaultOptions, ...options };
  
    return fetch(url, mergedOptions).then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error(text || "Network response was not ok");
        });
      }
  
      // Check if response is JSON
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return response.json();
      }
  
      return response.text();
    });
  }
  
  // Date formatting helpers
  function formatDateTime(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
  
    return `${year}${month}${day}${hours}${minutes}${seconds}`;
  }
  
  function formatDateTimeDisplay(dateString) {
    // Parse yyyymmddhhmmss format
    if (dateString.length === 14) {
      const year = dateString.substring(0, 4);
      const month = dateString.substring(4, 6);
      const day = dateString.substring(6, 8);
      const hours = dateString.substring(8, 10);
      const minutes = dateString.substring(10, 12);
      const seconds = dateString.substring(12, 14);
  
      const date = new Date(
        `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
      );
      return date.toLocaleString();
    }
  
    return dateString;
  }
  
  // Loading indicator
  function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML =
      '<div class="flex justify-center items-center p-4"><div class="spinner"></div></div>';
  }
  
  // Export functions for use in other scripts
  window.showNotification = showNotification;
  window.validateRequired = validateRequired;
  window.showFieldError = showFieldError;
  window.clearFieldError = clearFieldError;
  window.apiRequest = apiRequest;
  window.formatDateTime = formatDateTime;
  window.formatDateTimeDisplay = formatDateTimeDisplay;
  window.showLoading = showLoading;