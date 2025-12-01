document.addEventListener("DOMContentLoaded", () => {

  console.log("checkout.js cargado correctamente");

  let cart = JSON.parse(localStorage.getItem('cart') || '[]');

  function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
  }

  function money(n) {
    return '$' + Number(n || 0).toLocaleString('es-CL');
  }

  function renderCart() {
    const wrap = document.getElementById('cart');

    if (!cart.length) {
      wrap.innerHTML = '<div class="alert alert-warning">Tu carrito está vacío. Agrega productos desde el menú.</div>';
      document.getElementById('btn-submit').disabled = true;
      return;
    }

    document.getElementById('btn-submit').disabled = false;

    let total = 0;

    const rows = cart.map((item, idx) => {
      const subtotal = item.qty * item.unit_price;
      item.subtotal = subtotal;
      total += subtotal;

      return `
      <tr>
        <td>${item.product_name}</td>

        <td>
          <div class="qty-controls">
            <button class="qty-btn" data-act="dec" data-idx="${idx}">−</button>
            <span class="qty-value">${item.qty}</span>
            <button class="qty-btn" data-act="inc" data-idx="${idx}">+</button>
          </div>
        </td>

        <td class="price">${money(item.unit_price)}</td>
        <td class="price">${money(subtotal)}</td>
        <td><button class="btn btn-secondary btn-sm" data-act="del" data-idx="${idx}">Eliminar</button></td>
      </tr>`;
    }).join('');

    wrap.innerHTML = `
      <div class="table-responsive">
        <table class="cart-table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Cantidad</th>
              <th>Precio</th>
              <th>Subtotal</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
          <tfoot>
            <tr class="total-row">
              <td colspan="3">Total</td>
              <td>${money(total)}</td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>`;

    wrap.querySelectorAll("button[data-act]").forEach(btn => {
      btn.addEventListener("click", () => {
        const i = Number(btn.dataset.idx);
        const act = btn.dataset.act;

        if (act === "inc") cart[i].qty++;
        if (act === "dec") cart[i].qty = Math.max(1, cart[i].qty - 1);
        if (act === "del") cart.splice(i, 1);

        saveCart();
        renderCart();
      });
    });
  }

  renderCart();

  document.getElementById("btn-clear").addEventListener("click", () => {
    if (confirm("¿Vaciar carrito?")) {
      cart = [];
      saveCart();
      renderCart();
    }
  });

});
