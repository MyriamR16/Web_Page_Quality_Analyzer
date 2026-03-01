window.addEventListener("DOMContentLoaded", () => {
  document.cookie = "weakCookieA=1; path=/";
  document.cookie = "weakCookieB=1; path=/; SameSite=None";
  document.cookie = "weakCookieC=1; path=/; SameSite=Lax";
  console.log("Weak cookies created for security checks");
});
