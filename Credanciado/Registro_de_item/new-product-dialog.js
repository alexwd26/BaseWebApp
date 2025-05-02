class NewProductDialog {
  constructor() {
    this.dialog = document.getElementById("newProductDialog");
    this.form = document.getElementById("productForm");
    this.uploadZone = document.getElementById("uploadZone");
    this.fileInput = document.getElementById("productImage");
    this.additionalsList = document.getElementById("additionalsList");
    this.addButton = document.getElementById("addAdditionalItem");
    this.closeButton = document.getElementById("closeDialog");
    this.cancelButton = document.getElementById("cancelButton");

    this.additionalItems = [];

    this.initializeEventListeners();
  }

  initializeEventListeners() {
    // Dialog controls
    this.closeButton.addEventListener("click", () => this.closeDialog());
    this.cancelButton.addEventListener("click", () => this.closeDialog());

    // Form submission
    this.form.addEventListener("submit", (e) => this.handleSubmit(e));

    // File upload
    this.uploadZone.addEventListener("click", () => this.fileInput.click());
    this.uploadZone.addEventListener("dragover", (e) => this.handleDragOver(e));
    this.uploadZone.addEventListener("drop", (e) => this.handleDrop(e));
    this.fileInput.addEventListener("change", (e) => this.handleFileSelect(e));

    // Additional items
    this.addButton.addEventListener("click", () => this.addAdditionalItem());
  }

  openDialog() {
    this.dialog.showModal();
  }

  closeDialog() {
    this.dialog.close();
    this.resetForm();
  }

  resetForm() {
    this.form.reset();
    this.additionalItems = [];
    this.additionalsList.innerHTML = "";
  }

  handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    this.uploadZone.style.borderColor = "#4318d1";
  }

  handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    this.uploadZone.style.borderColor = "#e5e7eb";

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      this.fileInput.files = files;
      this.handleFileSelect({ target: this.fileInput });
    }
  }

  handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith("image/")) {
      // Handle file upload
      this.uploadFile(file);
    }
  }

  async uploadFile(file) {
    try {
      const formData = new FormData();
      formData.append("image", file);

      const response = await fetch(
        "http://15.228.148.198:8000/api/upload-image",
        {
          method: "POST",
          body: formData,
        },
      );

      if (!response.ok) {
        throw new Error("Failed to upload image");
      }

      const data = await response.json();
      // Store the image URL or handle as needed
      this.uploadedImageUrl = data.url;
    } catch (error) {
      console.error("Error uploading image:", error);
      // Handle error appropriately
    }
  }

  addAdditionalItem() {
    const itemIndex = this.additionalItems.length;

    const itemDiv = document.createElement("div");
    itemDiv.className = "additional-item";

    const nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.className = "form-input additional-name";
    nameInput.placeholder = "Nome do adicional";
    nameInput.required = true;

    const priceInput = document.createElement("input");
    priceInput.type = "number";
    priceInput.className = "form-input additional-price";
    priceInput.placeholder = "Preço";
    priceInput.step = "0.01";
    priceInput.required = true;

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "remove-button";
    removeButton.textContent = "×";
    removeButton.addEventListener("click", () =>
      this.removeAdditionalItem(itemIndex),
    );

    itemDiv.appendChild(nameInput);
    itemDiv.appendChild(priceInput);
    itemDiv.appendChild(removeButton);

    this.additionalsList.appendChild(itemDiv);
    this.additionalItems.push({ name: "", price: "" });

    nameInput.addEventListener("change", (e) => {
      this.additionalItems[itemIndex].name = e.target.value;
    });

    priceInput.addEventListener("change", (e) => {
      this.additionalItems[itemIndex].price = e.target.value;
    });
  }

  removeAdditionalItem(index) {
    this.additionalItems.splice(index, 1);
    this.additionalsList.children[index].remove();
    // Update indices for remaining items
    this.updateAdditionalItemsIndices();
  }

  updateAdditionalItemsIndices() {
    const items = this.additionalsList.children;
    for (let i = 0; i < items.length; i++) {
      const removeButton = items[i].querySelector(".remove-button");
      removeButton.onclick = () => this.removeAdditionalItem(i);
    }
  }

  async handleSubmit(e) {
    e.preventDefault();

    const formData = {
      name: document.getElementById("productName").value,
      category: document.getElementById("productCategory").value,
      price: parseFloat(document.getElementById("productPrice").value),
      description: document.getElementById("productDescription").value,
      image: this.uploadedImageUrl,
      additionalItems: this.additionalItems,
    };

    try {
      const response = await fetch("http://15.228.148.198:8000/api/menus", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Failed to create product");
      }

      // Handle successful creation
      this.closeDialog();
      // Optionally trigger a refresh or update of the products list
    } catch (error) {
      console.error("Error creating product:", error);
      // Handle error appropriately
    }
  }
}

// Initialize the dialog
const newProductDialog = new NewProductDialog();

// Export for use in other modules if needed
export { NewProductDialog };
