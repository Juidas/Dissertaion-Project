document.addEventListener("DOMContentLoaded", () => {
  fetch("navbar.html")
    .then(response => response.text())
    .then(data => {
      const navContainer = document.createElement("div");
      navContainer.innerHTML = data;
      document.body.prepend(navContainer);

      const token = localStorage.getItem("token");

      window.setTimeout(() => {
        const navLogin = document.getElementById("nav-login");
        const navRegister = document.getElementById("nav-register");
        const navLogout = document.getElementById("nav-logout");
        const navCart = document.getElementById("nav-cart");
        const navOrders = document.getElementById("nav-orders");
        const navAdmin = document.getElementById("nav-admin");

        if (token) {
          navLogin?.classList.add("d-none");
          navRegister?.classList.add("d-none");
          navLogout?.classList.remove("d-none");
          navCart?.classList.remove("d-none");
          navOrders?.classList.remove("d-none");

          try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if (payload.role === "admin") {
              navAdmin?.classList.remove("d-none");
            } else {
              navAdmin?.classList.add("d-none");
            }
          } catch (e) {
            navAdmin?.classList.add("d-none");
          }
        } else {
          navLogin?.classList.remove("d-none");
          navRegister?.classList.remove("d-none");
          navLogout?.classList.add("d-none");
          navCart?.classList.add("d-none");
          navOrders?.classList.add("d-none");
          navAdmin?.classList.add("d-none");
        }

        // Attach modal triggers AFTER navbar loads
        navLogin?.addEventListener("click", (e) => {
          e.preventDefault();
          isLogin = true;
          document.getElementById("authModalTitle").textContent = "Login";
          new bootstrap.Modal(document.getElementById("authModal")).show();
        });

        navRegister?.addEventListener("click", (e) => {
          e.preventDefault();
          isLogin = false;
          document.getElementById("authModalTitle").textContent = "Register";
          new bootstrap.Modal(document.getElementById("authModal")).show();
        });

        navLogout?.addEventListener("click", () => {
          localStorage.removeItem("token");
          location.reload();
        });

      }, 100);
    });
});
