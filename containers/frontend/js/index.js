let isLogin = true;

document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  // Load products
  fetch(`${BASE_URLS.product}/`)
    .then(res => res.json())
    .then(products => {
      const list = document.getElementById("product-list");
      products.forEach(p => {
        const div = document.createElement("div");
        div.className = "col-md-4 mb-3";
        div.innerHTML = `
          <div class="card">
            <div class="card-body">
              <h5>${p.name}</h5>
              <p>${p.description}</p>
              <strong>$${p.price}</strong><br>
              <button class="btn btn-sm btn-success mt-2" onclick="addToCart(${p.id})">Add to Cart</button>
            </div>
          </div>`;
        list.appendChild(div);
      });
    });

  // Auth modal toggle
  document.getElementById("authToggle").addEventListener("click", () => {
    isLogin = !isLogin;
    document.getElementById("authModalTitle").textContent = isLogin ? "Login" : "Register";
    document.getElementById("authToggle").textContent = isLogin ? "Don't have an account? Register" : "Already have an account? Login";
  });

  // Auth form handler
  document.getElementById("authForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("auth-username").value;
    const password = document.getElementById("auth-password").value;
    const endpoint = isLogin ? "login" : "register";
   
    const headers = {
      "Content-Type": "application/json"
    };
  
    if (endpoint === "register") {
      headers["x-api-key"] = "registration-secret-key"; 
    }

    const res = await fetch(`${BASE_URLS.auth}/${endpoint}`, {
      method: "POST",
      headers,
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (res.ok && endpoint === "login") {
      localStorage.setItem("token", data.access_token);
      alert("Login successful");
      location.reload();
    } else if (res.ok && endpoint === "register") {
      alert("Registration successful. You can now log in.");
    } else {
      alert(data.message || "Authentication failed");
    }
  });
});

function addToCart(productId) {
  const token = localStorage.getItem("token");
  if (!token) {
    const modal = new bootstrap.Modal(document.getElementById('authModal'));
    modal.show();
    return;
  }

  fetch(`${BASE_URLS.cart}/add`, {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ product_id: productId, quantity: 1 })
  })
    .then(res => res.json())
    .then(data => alert(data.message || "Added to cart"));
}

function logout() {
  localStorage.removeItem("token");
  location.reload();
}

// Show auth modal when clicking Login/Register in navbar
document.getElementById("nav-login").addEventListener("click", (e) => {
  e.preventDefault();
  isLogin = true;
  document.getElementById("authModalTitle").textContent = "Login";
  const modal = new bootstrap.Modal(document.getElementById("authModal"));
  modal.show();
});

document.getElementById("nav-register").addEventListener("click", (e) => {
  e.preventDefault();
  isLogin = false;
  document.getElementById("authModalTitle").textContent = "Register";
  const modal = new bootstrap.Modal(document.getElementById("authModal"));
  modal.show();
});
