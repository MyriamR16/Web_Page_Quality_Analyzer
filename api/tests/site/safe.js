window.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("safeButton");
  if (button) {
    button.addEventListener("click", () => {
      console.log("safe button clicked");
    });
  }

  const form = document.getElementById("safeForm");
  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      console.log("safe form submit");
    });
  }
});
