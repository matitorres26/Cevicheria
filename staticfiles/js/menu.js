// --- Scroll suave ---
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const t = document.querySelector(a.getAttribute('href'));
    if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth' }); }
  });
});

// --- Carrito ---
let cart = JSON.parse(localStorage.getItem('cart') || '[]');
function saveCart() { localStorage.setItem('cart', JSON.stringify(cart)); }

// --- Detectar si es Handroll ---
function isHandrollName(name) {
  return /hand[\s-]?roll/i.test(name || '');
}

// --- Detectar categoría ---
function detectCategory(prod) {
  const cat = (prod.category || '').toString().toLowerCase();
  const name = (prod.name || '').toString().toLowerCase();
  if (cat.includes('ceviche') || name.includes('ceviche')) return 'ceviche';
  if (cat.includes('sushi') || name.includes('sushi') || name.includes('roll') || name.includes('promo') || name.includes('promo')) return 'sushi';
  return 'otros';
}

// --- Renderizar una sección ---
function renderSection(containerId, items, allProducts) {
  const html = items.map(p => {
    const index = allProducts.indexOf(p);
    return `
      <div class="card">
        <img src="${p.image_url || 'https://placehold.co/600x400'}" class="card-img-top" alt="${p.name}">
        <div class="card-body">
          <h5 class="card-title">${p.name}</h5>
          <p class="card-desc">${p.description || ''}</p>
          <p class="card-text">$${Number(p.price).toLocaleString()}</p>
          <button class="btn btn-outline-primary btn-add" data-index="${index}">Agregar</button>
        </div>
      </div>
    `;
  }).join('');
  document.getElementById(containerId).innerHTML = html;
}

// --- Render general de productos ---
function renderProducts(list) {
  const products = (list || []).filter(p => p.available !== false);
  const cev = [], sus = [], oth = [];

  products.forEach(p => {
    const cat = detectCategory(p);
    if (cat === 'ceviche') cev.push(p);
    else if (cat === 'sushi') sus.push(p);
    else oth.push(p);
  });

  renderSection('ceviches', cev, products);
  renderSection('sushi', sus, products);
  renderSection('otros', oth, products);

  document.querySelectorAll('.btn-add').forEach(btn => {
    btn.onclick = () => {
      const i = parseInt(btn.dataset.index);
      const prod = products[i];
      if (isHandrollName(prod.name)) {
        openHandrollModal();
      } else {
        openQtyModalForProduct(prod);
      }
    };
  });
}

// --- Modal cantidad ---
let selectedProduct = null, selectedQty = 1;
const qtyModal = document.getElementById('qtyModal');
const modalProductName = document.getElementById('modalProductName');
const qtyValue = document.getElementById('qtyValue');

document.getElementById('incQty').onclick = () => { selectedQty++; qtyValue.textContent = selectedQty; };
document.getElementById('decQty').onclick = () => { if (selectedQty > 1) selectedQty--; qtyValue.textContent = selectedQty; };
document.getElementById('closeModal').onclick = () => qtyModal.classList.remove('open');

function openQtyModalForProduct(prod) {
  selectedProduct = prod;
  selectedQty = 1;
  modalProductName.textContent = `${prod.name} — $${Number(prod.price).toLocaleString()}`;
  qtyValue.textContent = 1;
  qtyModal.classList.add('open');
}

document.getElementById('addToCartModal').onclick = () => {
  if (!selectedProduct) return;
  cart.push({ product_name: selectedProduct.name, qty: selectedQty, unit_price: selectedProduct.price, subtotal: selectedProduct.price * selectedQty });
  saveCart();
  qtyModal.classList.remove('open');
}

// --- Modal Handroll ---
const handrollOptions = [
  { name: 'Handroll Kanikama (Queso,Cebollin)', price: 3000 },
  { name: 'Handroll Pollo (Queso,Cebollin)', price: 3500 },
  { name: 'Handroll Champiñón (Queso,Cebollin)', price: 3500 },
  { name: 'Handroll Choclito (Queso,Cebollin)', price: 3000 },
  { name: 'Handroll Palmito(Queso,Cebollin)', price: 3000 },
  { name: 'Handroll Camarón (Queso,Cebollin)', price: 4000 },
  { name: 'Handroll Salmón (Queso,Cebollin)', price: 4500 },
];

const handrollModal = document.getElementById('handrollModal');
const handrollForm = document.getElementById('handrollForm');
const closeHandrollModal = document.getElementById('closeHandrollModal');

function buildHandrollForm() {
  handrollForm.innerHTML = handrollOptions.map((opt, i) => `
    <label style="display:block;margin:8px 0;">
      <input type="radio" name="handrollType" value="${i}" ${i===0?'checked':''}>
      ${opt.name} — <b>$${opt.price.toLocaleString()}</b>
    </label>
  `).join('') + `
    <div style="margin-top:10px;">
      <label>Cantidad:</label><br>
      <input type="number" id="handrollQty" min="1" value="1" style="width:80px;text-align:center;">
    </div>
    <div style="margin-top:12px;">
      <button type="submit" class="btn btn-success">Agregar</button>
    </div>
  `;
}

document.getElementByById?.('handrollForm') || buildHandrollForm();

function openHandrollModal() { handrollModal.classList.add('open'); }
function closeHandroll() { handrollModal.classList.remove('open'); }
closeHandrollModal.onclick = closeHandroll;

window.addEventListener('click', e => {
  if (e.target === handrollModal) closeHandHandroll();
  if (e.target === qtyModal) qtyModal.classList.remove('open');
});

// --- Cargar productos ---
(async () => {
  try {
    const r = await fetch('/api/products/');
    const data = await r.json();
    renderProducts((data || []).map(p => ({ ...p, price: Number(p.price) || 0 })));
  } catch (err) {
    console.error('Error al cargar productos:', err);
  }
})();
