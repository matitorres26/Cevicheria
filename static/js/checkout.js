// checkout.js

document.addEventListener("DOMContentLoaded", () => {
  console.log("CHECKOUT JS: DOM listo");

  /* ============================================================
     UTILIDADES
     ============================================================ */
  const $ = (id) => document.getElementById(id);
  const money = (n) => "$" + Number(n || 0).toLocaleString("es-CL");

  console.log("FORM AL INICIO:", $("checkoutForm"));

  let cart = JSON.parse(localStorage.getItem("cart") || "[]");

  function saveCart() {
    localStorage.setItem("cart", JSON.stringify(cart));
  }

  /* ============================================================
     RENDER DEL CARRITO
     ============================================================ */
  function renderCart() {
    const wrap = $("cart");

    if (!cart.length) {
      wrap.innerHTML = `
        <div class="alert alert-warning">Tu carrito está vacío.</div>`;
      $("btn-submit").disabled = true;
      return;
    }

    $("btn-submit").disabled = false;

    let total = 0;
    const rows = cart
      .map((item, i) => {
        const subtotal = item.qty * item.unit_price;
        item.subtotal = subtotal;
        total += subtotal;

        return `
          <tr>
            <td>${item.product_name}</td>

            <td>
              <div class="qty-controls">
                <button class="qty-btn" data-act="dec" data-idx="${i}">−</button>
                <span>${item.qty}</span>
                <button class="qty-btn" data-act="inc" data-idx="${i}">+</button>
              </div>
            </td>

            <td>${money(item.unit_price)}</td>
            <td>${money(subtotal)}</td>

            <td>
              <button class="btn btn-secondary" data-act="del" data-idx="${i}">
                Eliminar
              </button>
            </td>
          </tr>`;
      })
      .join("");

    wrap.innerHTML = `
      <table class="cart-table">
        <thead>
          <tr>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Precio</th>
            <th>Subtotal</th>
            <th></th>
          </tr>
        </thead>

        <tbody>${rows}</tbody>

        <tfoot>
          <tr>
            <td colspan="3"><strong>Total</strong></td>
            <td>${money(total)}</td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    `;

    // botones de cantidad
    wrap.querySelectorAll("[data-act]").forEach((btn) => {
      btn.onclick = () => {
        const i = Number(btn.dataset.idx);
        const act = btn.dataset.act;

        if (act === "inc") cart[i].qty++;
        if (act === "dec") cart[i].qty = Math.max(1, cart[i].qty - 1);
        if (act === "del") cart.splice(i, 1);

        saveCart();
        renderCart();
      };
    });
  }

  renderCart();

  /* ============================================================
     LIMPIAR CARRITO
     ============================================================ */
  $("btn-clear").onclick = () => {
    if (!cart.length) return;
    if (confirm("¿Vaciar carrito completo?")) {
      cart = [];
      saveCart();
      renderCart();
    }
  };

  /* ============================================================
     VALIDACIÓN PREVIA AL ENVÍO
     ============================================================ */
  function validateForm(fd) {
    if (!fd.get("name").trim()) return "Debe ingresar su nombre.";
    return null;
  }

  /* ============================================================
     SUBMIT PRINCIPAL
     ============================================================ */
  const form = $("checkoutForm");

  if (!form) {
    console.error("No se encontró el formulario #checkoutForm");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();            // ⬅️ BLOQUEA el submit normal
    console.log("SUBMIT INTERCEPTADO");

    const msg = $("msg");
    msg.innerHTML = "";
    $("btn-submit").disabled = true;
    $("btn-submit").textContent = "Enviando...";

    if (!cart.length) {
      msg.innerHTML = `<div class="alert alert-warning">El carrito está vacío.</div>`;
      $("btn-submit").disabled = false;
      $("btn-submit").textContent = "Enviar Pedido";
      return;
    }

    const fd = new FormData(e.target);

    // validación
    const error = validateForm(fd);
    if (error) {
      msg.innerHTML = `<div class="alert alert-danger">${error}</div>`;
      $("btn-submit").disabled = false;
      $("btn-submit").textContent = "Enviar Pedido";
      return;
    }

    const payment_method = fd.get("payment_method");

    const payload = {
      name: fd.get("name"),
      phone: fd.get("phone") || "",
      email: fd.get("email") || "",
      address: fd.get("address") || "",
      payment_method,
      items: cart.map((i) => ({
        product_name: i.product_name,
        qty: i.qty,
        unit_price: i.unit_price,
        subtotal: i.qty * i.unit_price,
      })),
    };

    /* ------------------------------
       ENVIAR ORDEN
       ------------------------------ */
    let res;
    try {
      res = await fetch("/api/public/orders/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": fd.get("csrfmiddlewaretoken"),
        },
        body: JSON.stringify(payload),
      });
    } catch (err) {
      console.error("Error de conexión:", err);
      msg.innerHTML = `<div class="alert alert-danger">Error de conexión.</div>`;
      $("btn-submit").disabled = false;
      $("btn-submit").textContent = "Enviar Pedido";
      return;
    }

    if (!res.ok) {
      msg.innerHTML = `<div class="alert alert-danger">Error al enviar pedido.</div>`;
      $("btn-submit").disabled = false;
      $("btn-submit").textContent = "Enviar Pedido";
      return;
    }

    const order = await res.json();
    console.log("ORDER CREADA:", order);

    /* ------------------------------
       PAGO WEBPAY
       ------------------------------ */
    if (payment_method === "WEBPAY") {
      const wp = await fetch(`/api/webpay/init/${order.id}/`);
      const data = await wp.json();

      if (data.url && data.token) {
        const f = document.createElement("form");
        f.method = "POST";
        f.action = data.url;
        f.innerHTML = `<input type="hidden" name="token_ws" value="${data.token}">`;
        document.body.appendChild(f);
        f.submit();
        return;
      }
    }

    /* ------------------------------
       MOSTRAR MODAL
       ------------------------------ */
    llenarBoleta(order);
    $("modalGracias").style.display = "flex";
    iniciarTimerEntrega();

    // limpiar carrito
    cart = [];
    saveCart();
    renderCart();

    msg.innerHTML = `<div class="alert alert-success">Pedido enviado correctamente.</div>`;
    $("btn-submit").disabled = false;
    $("btn-submit").textContent = "Enviar Pedido";
  });

  /* ============================================================
     TIMER
     ============================================================ */
  async function calcularTiempoEstimado() {
    const r = await fetch("/api/public/orders/active-count/");
    const { count } = await r.json();

    const hora = new Date().getHours();
    let base = (hora >= 12 && hora <= 15) || (hora >= 19 && hora <= 21) ? 30 : 25;

    let extra = count <= 5 ? count : count <= 15 ? 10 + (count - 6) : 25;

    let total = base + extra;
    return Math.max(20, Math.min(total, 55));
  }

  async function iniciarTimerEntrega() {
    let m = await calcularTiempoEstimado();
    let s = 0;

    const el = $("timerTexto");
    el.textContent = `${m}m 00s`;

    const interval = setInterval(() => {
      if (s === 0) {
        if (m === 0) {
          clearInterval(interval);
          el.textContent = "¡Listo!";
          return;
        }
        m--;
        s = 59;
      } else s--;

      el.textContent = `${m}m ${s.toString().padStart(2, "0")}s`;
    }, 1000);
  }

  /* ============================================================
     MODAL + BOLETA
     ============================================================ */
  window.cerrarModalGracias = function () {
    $("modalGracias").style.display = "none";
    window.location.href = "/";
  };

  function llenarBoleta(order) {
    const fecha = new Date().toLocaleString("es-CL");

    $("b_id_header").textContent = order.id;
    $("b_nombre").textContent = order.name;
    $("b_fecha").textContent = fecha;
    $("b_total").textContent = money(order.total_price);

    let extra = "";

    if (order.address?.trim()) {
      extra += `<p><strong>Dirección:</strong> ${order.address}</p>`;
    } else {
      extra += `<p><strong>Retiro en local</strong></p>`;
    }

    $("extra-info").innerHTML = extra;

    $("b_items").innerHTML = order.items
      .map(
        (i) => `
        <tr>
          <td>${i.qty}×</td>
          <td>${i.product_name}</td>
          <td style="text-align:right">${money(i.subtotal)}</td>
        </tr>`
      )
      .join("");
  }

  window.imprimirBoleta = function () {
    const html = `
      <html>
      <head>
        <title>Boleta</title>
        <style>
          body { font-family: Poppins, sans-serif; padding: 20px; }
          h2 { color: #92ac44; }
        </style>
      </head>
      <body>
        <h2>Boleta de Compra</h2>
        Pedido N° ${$("b_id_header").innerText}<br>
        Cliente: ${$("b_nombre").innerText}<br>
        Fecha: ${$("b_fecha").innerText}<br><br>
        <table>${$("b_items").innerHTML}</table>
        <h3>Total: ${$("b_total").innerText}</h3>
      </body>
      </html>
    `;

    const win = window.open("", "_blank");
    win.document.write(html);
    win.document.close();

    setTimeout(() => win.print(), 300);
  };
});
