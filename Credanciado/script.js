document.addEventListener("DOMContentLoaded", function () {
  // Navigation handling
  const navItems = document.querySelectorAll(".nav-item");
  const views = document.querySelectorAll(".view");

  navItems.forEach((item) => {
    item.addEventListener("click", () => {
      // Remove active class from all items
      navItems.forEach((nav) => nav.classList.remove("active"));
      views.forEach((view) => view.classList.remove("active"));

      // Add active class to clicked item
      item.classList.add("active");

      // Show corresponding view
      const page = item.dataset.page;
      const view = document.getElementById(`${page}-view`);
      if (view) view.classList.add("active");
    });
  });

  // Order status update handling
  const actionButtons = document.querySelectorAll(".action-button");

  actionButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const orderCard = this.closest(".order-card");
      const currentSection = this.closest(".order-section");
      const nextSection = currentSection.nextElementSibling;

      if (nextSection) {
        const orderList = nextSection.querySelector(".order-list");
        orderList.appendChild(orderCard);

        // Update order counts
        updateOrderCounts();
      }
    });
  });

  function updateOrderCounts() {
    document.querySelectorAll(".order-section").forEach((section) => {
      const count = section.querySelectorAll(".order-card").length;
      section.querySelector(".order-count").textContent =
        `${count} pedido${count !== 1 ? "s" : ""}`;
    });
  }
});
