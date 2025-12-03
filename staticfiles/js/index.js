/* ============================
   Cargar pedidos desde API
============================ */
async function loadOrders() {
  try {
    const res = await fetch("/api/orders/");
    const data = await res.json();

    const wrap = document.getElementById("orders");
    wrap.innerHTML = "";

    data.forEach(o => {
      wrap.innerHTML += `
        <div class="order-card">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h5 class="order-title">🧾 ORDEN #${o.id}</h5>
            <span class="badge ${getStatusClass(o.status)}">${o.status}</span>
          </div>

          <p class="order-subtitle">👤 Cliente: <strong>${o.customer}</strong></p>

          <ul class="order-items">
            ${(o.items || [])
              .map(i => `
                <li>${i.qty}× ${i.product_name} — <strong>$${i.subtotal}</strong></li>
              `)
              .join("")}
          </ul>

          <div class="order-total">
            Total: $${o.total_price}
          </div>
        </div>
      `;
    });
  } catch (err) {
    console.error("Error cargando pedidos:", err);
  }
}

/* ============================
   Clases según estado
============================ */
function getStatusClass(status) {
  const s = status.toLowerCase();
  if (s.includes("pend")) return "bg-warning text-dark";
  if (s.includes("prep")) return "bg-info text-dark";
  if (s.includes("listo")) return "bg-success";
  if (s.includes("entregado")) return "bg-secondary";
  return "bg-dark";
}

/* ============================
   Cargar al inicio
============================ */
loadOrders();

/* ============================
   WebSocket tiempo real
============================ */
const wsScheme = location.protocol === "https:" ? "wss" : "ws";
const wsURL = `${wsScheme}://${location.host}/ws/orders/`;
const ws = new WebSocket(wsURL);

ws.onopen = () => console.log("🔌 WebSocket conectado");
ws.onerror = err => console.error("❌ Error en WS:", err);
ws.onclose = () => console.warn("⚠️ WebSocket desconectado");

ws.onmessage = (e) => {
  try {
    const data = JSON.parse(e.data);
    if (data.type === "new_order") {
      console.log("📦 Nuevo pedido:", data.order);
      loadOrders();
    }
  } catch (err) {
    console.error("❌ Error procesando WS:", err);
  }
};