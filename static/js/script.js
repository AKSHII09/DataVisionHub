/* ===============================================================
   🌐 Data Vision Hub – Modern Interactive Script (2025 Edition)
   Author: ChatGPT
   Description: Dynamic UI interactions for analytics dashboard
   =============================================================== */

document.addEventListener("DOMContentLoaded", () => {
  /* -------- 1️⃣ Auto-hide Flash Messages -------- */
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 600);
    }, 4000);
  });

  /* -------- 2️⃣ File Upload Preview -------- */
  const uploadInput = document.querySelector("input[type='file']");
  if (uploadInput) {
    uploadInput.addEventListener("change", (e) => {
      const fileName = e.target.files[0]?.name;
      if (fileName) {
        let label = document.querySelector("#file-name");
        if (!label) {
          label = document.createElement("div");
          label.id = "file-name";
          label.style.marginTop = "8px";
          label.style.fontSize = "0.9rem";
          label.style.color = "#bfbfff";
          uploadInput.parentNode.appendChild(label);
        }
        label.textContent = `📄 ${fileName}`;
      }
    });
  }

  /* -------- 3️⃣ Password Strength Indicator -------- */
  const passwordInput = document.querySelector("input[name='password']");
  if (passwordInput) {
    const strengthBar = document.createElement("div");
    strengthBar.style.height = "5px";
    strengthBar.style.borderRadius = "5px";
    strengthBar.style.marginTop = "6px";
    strengthBar.style.transition = "0.3s ease";
    passwordInput.insertAdjacentElement("afterend", strengthBar);

    passwordInput.addEventListener("input", () => {
      const val = passwordInput.value;
      let score = 0;

      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[a-z]/.test(val)) score++;
      if (/\d/.test(val)) score++;
      if (/[!@#$%^&*(),.?":{}|<>]/.test(val)) score++;

      const colors = ["#ff4e4e", "#ff8c00", "#fcd307", "#8efc7d", "#00e676"];
      strengthBar.style.width = `${(score / 5) * 100}%`;
      strengthBar.style.background = colors[score - 1] || "transparent";
    });
  }

  /* -------- 4️⃣ Confirm Password Validation -------- */
  const confirmInput = document.querySelector("input[name='confirm_password']");
  if (confirmInput && passwordInput) {
    confirmInput.addEventListener("input", () => {
      if (confirmInput.value !== passwordInput.value) {
        confirmInput.style.borderColor = "#ff6b6b";
      } else {
        confirmInput.style.borderColor = "#4caf50";
      }
    });
  }

  /* -------- 5️⃣ Smooth Scroll for Anchor Links -------- */
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });

  /* -------- 6️⃣ Dark/Light Mode Toggle -------- */
  const toggleBtn = document.createElement("button");
  toggleBtn.className = "btn btn-outline-light position-fixed";
  toggleBtn.style.bottom = "25px";
  toggleBtn.style.right = "25px";
  toggleBtn.style.zIndex = "999";
  toggleBtn.style.borderRadius = "50%";
  toggleBtn.style.padding = "10px 13px";
  toggleBtn.innerHTML = "🌙";
  document.body.appendChild(toggleBtn);

  // Apply saved theme
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.classList.add("light-mode");
    toggleBtn.innerHTML = "☀️";
  }

  toggleBtn.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");
    const isLight = document.body.classList.contains("light-mode");
    toggleBtn.innerHTML = isLight ? "☀️" : "🌙";
    localStorage.setItem("theme", isLight ? "light" : "dark");
  });

  /* -------- 7️⃣ Button Ripple Effect -------- */
  document.querySelectorAll(".btn").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      const ripple = document.createElement("span");
      ripple.classList.add("ripple");
      this.appendChild(ripple);

      const max = Math.max(this.offsetWidth, this.offsetHeight);
      ripple.style.width = ripple.style.height = max + "px";
      ripple.style.left = e.offsetX - max / 2 + "px";
      ripple.style.top = e.offsetY - max / 2 + "px";

      setTimeout(() => ripple.remove(), 600);
    });
  });
});

/* ===============================================================
   🌗 Light Mode Styles (activated via JS toggle)
   =============================================================== */
const lightModeStyles = `
body.light-mode {
  background: linear-gradient(135deg, #f8f9fc, #ffffff);
  color: #1a1a1a;
}
body.light-mode .card {
  background: rgba(255, 255, 255, 0.9);
  color: #1a1a1a;
  border: 1px solid rgba(0, 0, 0, 0.1);
}
body.light-mode .navbar {
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}
body.light-mode .btn-primary {
  background: linear-gradient(135deg, #6a5eff, #9b86ff);
}
body.light-mode .upload-box {
  border-color: #8a79ff;
}
body.light-mode .table th {
  background: linear-gradient(135deg, #6a5eff, #9b86ff);
}
.ripple {
  position: absolute;
  border-radius: 50%;
  transform: scale(0);
  animation: ripple-effect 0.6s linear;
  background: rgba(255, 255, 255, 0.6);
  pointer-events: none;
}
@keyframes ripple-effect {
  to {
    transform: scale(3);
    opacity: 0;
  }
}
`;

// Inject light mode CSS
const styleEl = document.createElement("style");
styleEl.innerHTML = lightModeStyles;
document.head.appendChild(styleEl);
