/* ======================================
   UTILIDADES
====================================== */
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const apiProductsUrl = "/api/products/";
let cart = JSON.parse(localStorage.getItem("cart") || "[]");

const saveCart = () => localStorage.setItem("cart", JSON.stringify(cart));
const money = (n) => Number(n || 0).toLocaleString("es-CL");

/* ======================================
   SCROLL SUAVE
====================================== */
$$('a[href^="#"]').forEach((a) => {
  a.onclick = (e) => {
    const t = $(a.getAttribute("href"));
    if (t) {
      e.preventDefault();
      t.scrollIntoView({ behavior: "smooth" });
    }
  };
});

/* ======================================
   DETECTAR CATEGORÍAS & HANDROLL
====================================== */
const isHandrollName = (n) => /hand[\s-]?roll/i.test(n || "");

function detectCategory(prod) {
  const cat = (prod.category || "").toLowerCase();
  const name = (prod.name || "").toLowerCase();

  if (cat.includes("ceviche") || name.includes("ceviche")) return "ceviche";
  if (["sushi", "roll", "promo"].some((k) => name.includes(k) || cat.includes(k)))
    return "sushi";
  return "otros";
}

/* ======================================
   RENDER DE PRODUCTOS
====================================== */
function renderSection(containerId, items) {
  $(containerId).innerHTML = items
    .map(
      (p) => `
    <div class="card">
      <img src="${p.image_url || "https://placehold.co/600x400"}" class="card-img-top">
      <div class="card-body">
        <h5 class="card-title">${p.name}</h5>
        <p class="card-desc">${p.description || ""}</p>
        <p class="card-text">$${money(p.price)}</p>
        <button class="btn btn-outline-primary btn-add" data-id="${p.id}">Agregar</button>
      </div>
    </div>`
    )
    .join("");
}

function renderProducts(list) {
  const products = list.filter((p) => p.available !== false);

  const cev = products.filter((p) => detectCategory(p) === "ceviche");
  const sus = products.filter((p) => detectCategory(p) === "sushi");
  const oth = products.filter((p) => detectCategory(p) === "otros");

  renderSection("#ceviches", cev);
  renderSection("#sushi", sus);
  renderSection("#otros", oth);

  // Botones agregar
  $$(".btn-add").forEach((btn) => {
    btn.onclick = () => {
      const prod = products.find((p) => p.id == btn.dataset.id);
      if (!prod) return;

      isHandrollName(prod.name) ? openHandrollModal(prod) : openQtyModal(prod);
    };
  });
}

/* ======================================
   MODAL CANTIDAD
====================================== */
let selectedProduct = null;
let selectedQty = 1;

const qtyModal = $("#qtyModal");
const qtyValue = $("#qtyValue");
const modalProductName = $("#modalProductName");

function openQtyModal(prod) {
  selectedProduct = prod;
  selectedQty = 1;

  modalProductName.textContent = `${prod.name} — $${money(prod.price)}`;
  qtyValue.textContent = 1;

  qtyModal.classList.add("open");
}

$("#incQty").onclick = () => {
  selectedQty++;
  qtyValue.textContent = selectedQty;
};

$("#decQty").onclick = () => {
  if (selectedQty > 1) {
    selectedQty--;
    qtyValue.textContent = selectedQty;
  }
};

$("#closeModal").onclick = () => qtyModal.classList.remove("open");

$("#addToCartModal").onclick = () => {
  if (!selectedProduct) return;

  cart.push({
    product_name: selectedProduct.name,
    qty: selectedQty,
    unit_price: selectedProduct.price,
    subtotal: selectedProduct.price * selectedQty,
  });

  saveCart();
  qtyModal.classList.remove("open");
};

/* ======================================
   MODAL HANDROLL
====================================== */
const handrollOptions = [
  { name: "Handroll Kanikama (Queso,Cebollin)", price: 3000 },
  { name: "Handroll Pollo (Queso,Cebollin)", price: 3500 },
  { name: "Handroll Champiñón (Queso,Cebollin)", price: 3500 },
  { name: "Handroll Choclito (Queso,Cebollin)", price: 3000 },
  { name: "Handroll Palmito (Queso,Cebollin)", price: 3000 },
  { name: "Handroll Camarón (Queso,Cebollin)", price: 4000 },
  { name: "Handroll Salmón (Queso,Cebollin)", price: 4500 },
];

let handrollBaseProduct = null;

const handrollModal = $("#handrollModal");
const handrollForm = $("#handrollForm");

function openHandrollModal(prod) {
  handrollBaseProduct = prod;
  buildHandrollForm();
  handrollModal.classList.add("open");
}

function buildHandrollForm() {
  handrollForm.innerHTML = `
    ${handrollOptions
      .map(
        (opt, i) => `
      <label style="display:block;margin:8px 0;">
        <input type="radio" name="handrollType" value="${i}" ${
          i === 0 ? "checked" : ""
        }>
        ${opt.name} — <b>$${money(opt.price)}</b>
      </label>`
      )
      .join("")}
    
    <label style="margin-top:10px;">Cantidad:</label>
    <input type="number" id="handrollQty" value="1" min="1" style="width:80px;text-align:center;">

    <button type="submit" class="btn btn-success mt-3">Agregar</button>
  `;

  handrollForm.onsubmit = (e) => {
    e.preventDefault();

    const idx = Number(handrollForm.handrollType.value);
    const qty = Number($("#handrollQty").value);
    const opt = handrollOptions[idx];

    cart.push({
      product_name: opt.name,
      qty,
      unit_price: opt.price,
      subtotal: opt.price * qty,
    });

    saveCart();
    closeHandroll();
  };
}

const closeHandroll = () => handrollModal.classList.remove("open");
$("#closeHandrollModal").onclick = closeHandroll;

/* ======================================
   CLICK FUERA PARA CERRAR MODALES
====================================== */
window.addEventListener("click", (e) => {
  if (e.target === qtyModal) qtyModal.classList.remove("open");
  if (e.target === handrollModal) closeHandroll();
});

/* ======================================
   CARGAR PRODUCTOS
====================================== */
(async function loadProducts() {
  try {
    const r = await fetch(apiProductsUrl);
    const data = await r.json();
    renderProducts(data.map((p) => ({ ...p, price: Number(p.price) || 0 })));
  } catch (err) {
    console.error("Error cargando productos:", err);
  }
})();
