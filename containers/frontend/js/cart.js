document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("token");
  if (!token) return alert("Please login first.");

  const res = await fetch(`${BASE_URLS.cart}/`, {
    headers: { Authorization: "Bearer " + token }
  });

  const items = await res.json();
  const table = document.getElementById("cart-table");
  const tbody = table.querySelector("tbody");
  const totalDisplay = document.getElementById("total");

  if (!Array.isArray(items) || items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center">Cart is empty.</td></tr>`;
    totalDisplay.textContent = "$0.00";
    return;
  }

  // Optional: Group items by product_id if needed
  const grouped = {};
  items.forEach(item => {
    if (!grouped[item.product_id]) {
      grouped[item.product_id] = {
        product_name: item.product_name,
        price: item.price,
        quantity: item.quantity
      };
    } else {
      grouped[item.product_id].quantity += item.quantity;
    }
  });

  let total = 0;
  Object.values(grouped).forEach(item => {
    const row = document.createElement("tr");
    const subtotal = item.price * item.quantity;
    total += subtotal;

    row.innerHTML = `
      <td>${item.product_name}</td>
      <td>${item.quantity}</td>
      <td>$${item.price.toFixed(2)}</td>
      <td>$${subtotal.toFixed(2)}</td>
      <td><button class="btn btn-danger btn-sm" onclick="removeFromCart(${item.product_id})">&times;</button></td>
    `;
    tbody.appendChild(row);
  });

  totalDisplay.textContent = `$${total.toFixed(2)}`;
});

function removeFromCart(productId) {
  const token = localStorage.getItem("token");
  fetch(`${BASE_URLS.cart}/remove`, {
    method: "DELETE",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ product_id: productId })
  })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      location.reload();
    });
}

function checkout() {
  const token = localStorage.getItem("token");
  fetch(`${BASE_URLS.order}/checkout`, {
    method: "POST",
    headers: { Authorization: "Bearer " + token }
  })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      window.location.href = "orders.html";
    });
}
