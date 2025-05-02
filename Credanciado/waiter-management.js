(() => {
  const state = {
    waiters: [
      {
        id: 1,
        name: "John Smith",
        status: "active",
        tables: 4,
        orders: 12,
      },
      {
        id: 2,
        name: "Maria Garcia",
        status: "break",
        tables: 2,
        orders: 8,
      },
      {
        id: 3,
        name: "David Chen",
        status: "active",
        tables: 5,
        orders: 15,
      },
      {
        id: 4,
        name: "Sarah Johnson",
        status: "offline",
        tables: 0,
        orders: 0,
      },
      {
        id: 5,
        name: "Michael Wong",
        status: "active",
        tables: 3,
        orders: 10,
      },
      {
        id: 6,
        name: "Emily Brown",
        status: "break",
        tables: 1,
        orders: 4,
      },
    ],
    selectedStatus: "all",
    searchQuery: "",
  };

  // DOM Elements
  const searchInput = document.querySelector(".search-input");
  const statusFilter = document.querySelector(".status-filter");
  const tableBody = document.getElementById("waiters-table-body");

  // Event Listeners
  searchInput.addEventListener("input", (e) => {
    state.searchQuery = e.target.value;
    renderWaiters();
  });

  statusFilter.addEventListener("change", (e) => {
    state.selectedStatus = e.target.value;
    renderWaiters();
  });

  // Helper Functions
  function getStatusLabel(status) {
    return status.charAt(0).toUpperCase() + status.slice(1);
  }

  function toggleWaiterStatus(waiterId) {
    const waiter = state.waiters.find((w) => w.id === waiterId);
    if (waiter && waiter.status !== "offline") {
      waiter.status = waiter.status === "active" ? "break" : "active";
      renderWaiters();
    }
  }

  function updateStatsCounts() {
    document.querySelector(".total-count").textContent = state.waiters.length;
    document.querySelector(".active-count").textContent = state.waiters.filter(
      (w) => w.status === "active",
    ).length;
    document.querySelector(".break-count").textContent = state.waiters.filter(
      (w) => w.status === "break",
    ).length;
    document.querySelector(".offline-count").textContent = state.waiters.filter(
      (w) => w.status === "offline",
    ).length;
  }

  function renderWaiterRow(waiter) {
    const row = document.createElement("tr");

    // Name cell
    const nameCell = document.createElement("td");
    nameCell.innerHTML = `
            <div class="waiter-info">
                <span class="waiter-name">${waiter.name}</span>
                <span class="waiter-id">ID: ${waiter.id}</span>
            </div>
        `;

    // Status cell
    const statusCell = document.createElement("td");
    statusCell.innerHTML = `
            <span class="status-badge ${waiter.status}">
                ${getStatusLabel(waiter.status)}
            </span>
        `;

    // Tables cell
    const tablesCell = document.createElement("td");
    tablesCell.innerHTML = `<span class="table-value">${waiter.tables}</span>`;

    // Orders cell
    const ordersCell = document.createElement("td");
    ordersCell.innerHTML = `<span class="table-value">${waiter.orders}</span>`;

    // Actions cell
    const actionsCell = document.createElement("td");
    if (waiter.status !== "offline") {
      const actionButton = document.createElement("button");
      actionButton.className = "action-button";
      actionButton.textContent =
        waiter.status === "active" ? "Start Break" : "End Break";
      actionButton.onclick = () => toggleWaiterStatus(waiter.id);
      actionsCell.appendChild(actionButton);
    }

    row.append(nameCell, statusCell, tablesCell, ordersCell, actionsCell);
    return row;
  }

  function renderWaiters() {
    // Clear existing rows
    tableBody.innerHTML = "";

    // Filter waiters based on search and status
    const filteredWaiters = state.waiters.filter((waiter) => {
      const matchesSearch = waiter.name
        .toLowerCase()
        .includes(state.searchQuery.toLowerCase());
      const matchesStatus =
        state.selectedStatus === "all" ||
        waiter.status === state.selectedStatus;
      return matchesSearch && matchesStatus;
    });

    // Render filtered waiters
    filteredWaiters.forEach((waiter) => {
      tableBody.appendChild(renderWaiterRow(waiter));
    });

    // Update stats
    updateStatsCounts();
  }

  // Initial render
  renderWaiters();
})();
