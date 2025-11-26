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

// Export functions for use in other scripts
window.showNotification = showNotification;
