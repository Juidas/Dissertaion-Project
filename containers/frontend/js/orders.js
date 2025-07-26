document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("token");
  if (!token) return alert("Please login first.");

  const res = await fetch(`${BASE_URLS.order}/`, {
    headers: { Authorization: "Bearer " + token }
  });

  const orders = await res.json();
  const list = document.getElementById("order-list");

  if (!orders.length) {
    list.innerHTML = "<p>No orders yet.</p>";
    return;
  }

  orders.forEach(order => {
    const div = document.createElement("div");
    div.className = "border p-3 mb-3";

    const itemsList = order.items.map(i => {
      return `<li>${i.product_name} - ${i.quantity} x $${i.unit_price.toFixed(2)}</li>`;
    }).join('');

    div.innerHTML = `
      <h5>Order #${order.order_id ?? "N/A"} - $${order.total?.toFixed(2) ?? "0.00"}</h5>
      <small>Placed on: ${new Date(order.timestamp).toLocaleString()}</small>
      <ul>${itemsList}</ul>
    `;
    list.appendChild(div);
  });
});
