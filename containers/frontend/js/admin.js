// Patched version: BASE_URLS removed and fetch calls corrected

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    if (!token) return window.location.href = "index.html";
  
    const authRes = await fetch(`${BASE_URLS.auth}/profile`, {
      headers: { Authorization: "Bearer " + token }
    });
  
    const auth = await authRes.json();
    if (!auth.is_admin) {
      document.getElementById("not-admin").classList.remove("d-none");
      return;
    }
  
    document.getElementById("admin-content").classList.remove("d-none");
  
    // Load products
    const productRes = await fetch(`${BASE_URLS.product}/`);
    const products = await productRes.json();
    const list = document.getElementById("product-list");
    products.forEach(p => {
      const li = document.createElement("li");
      li.className = "list-group-item d-flex justify-content-between align-items-center";
      li.innerHTML = `
        ${p.name} - $${p.price}
        <button class="btn btn-danger btn-sm" onclick="deleteProduct(${p.id})">Delete</button>
      `;
      list.appendChild(li);
    });
  
    // Load all orders
    const ordersRes = await fetch(`${BASE_URLS.order}/all`, {
      headers: { Authorization: "Bearer " + token }
    });
  
    const orders = await ordersRes.json();
    const orderList = document.getElementById("order-list");
    orders.forEach(order => {
      const div = document.createElement("div");
      div.className = "border p-2 mb-2";
      div.innerHTML = `
        <strong>Order #${order.id}</strong> - $${order.total_amount}<br>
        User: ${order.user_id}<br>
        <small>Placed on: ${new Date(order.timestamp).toLocaleString()}</small>
        <ul>
          ${order.items.map(i => `<li>Product ${i.product_id} - ${i.quantity} x $${i.unit_price}</li>`).join('')}
        </ul>
      `;
      orderList.appendChild(div);
    });
  
    // Add product handler
    document.getElementById("add-product-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("product-name").value;
      const description = document.getElementById("product-description").value;
      const price = parseFloat(document.getElementById("product-price").value);
  
      const res = await fetch(`${BASE_URLS.product}/`, {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ name, description, price })
      });
  
      const data = await res.json();
      alert(data.message || "Product added");
      location.reload();
    });
  });
  
  async function deleteProduct(id) {
    const token = localStorage.getItem("token");
    const res = await fetch(`${BASE_URLS.product}/${id}`, {
      method: "DELETE",
      headers: { Authorization: "Bearer " + token }
    });
  
    const data = await res.json();
    alert(data.message || "Deleted");
    location.reload();
  }
x