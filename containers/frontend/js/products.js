// Patched version: BASE_URLS removed, fetch calls fixed

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
  
    fetch(`${BASE_URLS.product}/`)
      .then(res => res.json())
      .then(products => {
        const list = document.getElementById("product-list");
        products.forEach(p => {
          const div = document.createElement("div");
          div.className = "col-md-4 mb-3";
          const isLoggedIn = !!token;
          const actionButton = isLoggedIn
            ? `<button class="btn btn-sm btn-success mt-2" onclick="addToCart(${p.id})">Add to Cart</button>`
            : `<a href="login.html" class="btn btn-outline-primary btn-sm mt-2">Login to Add to Cart</a>`;
          div.innerHTML = `
            <div class="card">
              <div class="card-body">
                <h5>${p.name}</h5>
                <p>${p.description}</p>
                <strong>$${p.price}</strong><br>
                ${actionButton}
              </div>
            </div>`;
          list.appendChild(div);
        });
      });
  });
  
  function addToCart(productId) {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please login first.");
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
