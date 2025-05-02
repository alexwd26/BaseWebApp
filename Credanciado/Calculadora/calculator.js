(() => {
  const state = {
    display: "0",
    currentValue: "0",
    previousValue: null,
    operator: null,
    clearNext: false,

    calculate() {
      const prev = parseFloat(this.previousValue);
      const curr = parseFloat(this.currentValue);

      if (isNaN(prev) || isNaN(curr)) return curr;

      switch (this.operator) {
        case "+":
          return prev + curr;
        case "-":
          return prev - curr;
        case "×":
          return prev * curr;
        case "/":
          return curr !== 0 ? prev / curr : "Error";
        default:
          return curr;
      }
    },

    formatNumber(num) {
      if (num === "Error") return num;
      const maxLength = 10;
      const numStr = num.toString();

      if (numStr.length > maxLength) {
        return parseFloat(num).toPrecision(maxLength);
      }
      return numStr;
    },

    updateDisplay() {
      const displayElement = document.getElementById("displayValue");
      if (displayElement) {
        displayElement.textContent = this.formatNumber(this.display);
      }
    },

    handleNumber(num) {
      if (this.clearNext) {
        this.currentValue = num.toString();
        this.clearNext = false;
      } else {
        this.currentValue =
          this.currentValue === "0" ? num.toString() : this.currentValue + num;
      }
      this.display = this.currentValue;
      this.updateDisplay();
    },

    handleOperator(op) {
      if (this.previousValue === null) {
        this.previousValue = this.currentValue;
      } else if (!this.clearNext) {
        const result = this.calculate();
        this.previousValue = result.toString();
      }
      this.operator = op;
      this.clearNext = true;
      this.display = this.previousValue;
      this.updateDisplay();
    },

    handleEquals() {
      if (this.previousValue === null || this.clearNext) return;

      const result = this.calculate();
      this.display = result.toString();
      this.currentValue = result.toString();
      this.previousValue = null;
      this.operator = null;
      this.updateDisplay();
    },

    handleDecimal() {
      if (this.clearNext) {
        this.currentValue = "0.";
        this.clearNext = false;
      } else if (!this.currentValue.includes(".")) {
        this.currentValue += ".";
      }
      this.display = this.currentValue;
      this.updateDisplay();
    },

    clear() {
      this.display = "0";
      this.currentValue = "0";
      this.previousValue = null;
      this.operator = null;
      this.clearNext = false;
      this.updateDisplay();
    },
  };

  // Initialize calculator
  function initCalculator() {
    const calculator = document.querySelector(".calculator-wrapper");
    if (!calculator) return;

    // Number buttons
    calculator.querySelectorAll(".key-number").forEach((button) => {
      button.addEventListener("click", () => {
        state.handleNumber(button.textContent);
      });
    });

    // Operator buttons
    calculator.querySelectorAll(".key-operator").forEach((button) => {
      button.addEventListener("click", () => {
        state.handleOperator(button.textContent);
      });
    });

    // Special buttons
    calculator.querySelector(".key-clear").addEventListener("click", () => {
      state.clear();
    });

    calculator.querySelector(".key-equals").addEventListener("click", () => {
      state.handleEquals();
    });

    calculator.querySelector(".key-decimal").addEventListener("click", () => {
      state.handleDecimal();
    });

    calculator.querySelector(".key-divide").addEventListener("click", () => {
      state.handleOperator("/");
    });

    // Keyboard support
    document.addEventListener("keydown", (event) => {
      if (event.key >= "0" && event.key <= "9") {
        state.handleNumber(event.key);
      } else {
        switch (event.key) {
          case "+":
          case "-":
            state.handleOperator(event.key);
            break;
          case "*":
            state.handleOperator("×");
            break;
          case "/":
            state.handleOperator("/");
            break;
          case ".":
            state.handleDecimal();
            break;
          case "Enter":
          case "=":
            state.handleEquals();
            break;
          case "Escape":
            state.clear();
            break;
        }
      }
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCalculator);
  } else {
    initCalculator();
  }
})();
