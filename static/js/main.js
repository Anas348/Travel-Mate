// Mobile nav toggle
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".nav-toggle");
  const navbar = document.querySelector(".navbar");
  if (toggle && navbar) {
    toggle.addEventListener("click", () => navbar.classList.toggle("open"));
  }

  // Auth page tabs (login / register)
  const tabs = document.querySelectorAll(".auth-tab");
  const forms = document.querySelectorAll(".auth-form");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      forms.forEach((f) => f.setAttribute("hidden", ""));
      tab.classList.add("active");
      document.querySelector(`#${tab.dataset.target}`).removeAttribute("hidden");
    });
  });

  // Auto-dismiss flash messages
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => el.remove(), 5000);
  });

  // Repeatable "add another room" / "add another attraction" rows
  document.querySelectorAll("[data-repeat-add]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const templateId = btn.dataset.repeatAdd;
      const template = document.getElementById(templateId);
      const container = document.querySelector(btn.dataset.repeatTarget);
      if (template && container) {
        container.insertAdjacentHTML("beforeend", template.innerHTML);
      }
    });
  });

  document.body.addEventListener("click", (e) => {
    if (e.target.matches("[data-repeat-remove]")) {
      e.target.closest(".repeat-row").remove();
    }
  });
});
