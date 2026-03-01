window.addEventListener("DOMContentLoaded", () => {
  console.error("Synthetic console error: startup failed in module A");

  setTimeout(() => {
    throw new Error("Synthetic uncaught page error from setTimeout");
  }, 50);

  const button = document.getElementById("boomButton");
  if (button) {
    button.addEventListener("click", () => {
      throw new Error("Button click exception: synthetic");
    });
  }

  const form = document.getElementById("boomForm");
  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      throw new Error("Form submit exception: synthetic");
    });
  }
});
