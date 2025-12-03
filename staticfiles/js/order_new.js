/* ============================
   Obtener CSRF
============================ */
function getCookie(name) {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith(name + "="))
    ?.split("=")[1];
}

const csrftoken = getCookie("csrftoken");

/* ============================
   Enviar formulario
============================ */
document.getElementById("orderForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const fd = new FormData(e.target);
  const msg = document.getElementById("msg");

  const qty = Number(fd.get("qty"));
  const price = Number(fd.get("unit_price"));

  const payload = {
    customer: Number(fd.get("customer")),
    payment_method: "CASH",
    items: [
      {
        product_name: fd.get("product_name"),
        qty,
        unit_price: price,
        subtotal: qty * price,
      },
    ],
  };

  try {
    const res = await fetch("/api/orders/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      msg.innerHTML = `
        <div class="alert alert-success text-center">
          ✅ Pedido creado correctamente
        </div>`;
      e.target.reset();
    } else {
      const err = await res.json();
      msg.innerHTML = `
        <pre class="alert alert-danger">${JSON.stringify(err, null, 2)}</pre>
      `;
    }
  } catch (error) {
    msg.innerHTML = `
      <div class="alert alert-danger">
        ❌ Error de conexión con el servidor
      </div>
    `;
  }
});
