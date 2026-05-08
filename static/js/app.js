/* ============================================
   QUVVAT.MARKET — Frontend Application
   ============================================ */

// === CSRF helper ===
function getCookie(name) {
  const v = `; ${document.cookie}`;
  const parts = v.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}
const csrftoken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

async function api(url, opts = {}) {
  const headers = { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, ...(opts.headers || {}) };
  const res = await fetch(url, { ...opts, headers, credentials: 'same-origin' });
  let data = {};
  try { data = await res.json(); } catch (e) { }
  return { ok: res.ok, status: res.status, data };
}

// === Translations ===
const T = {
  uz: {
    nav_features: 'Afzalliklar', nav_contact: 'Aloqa',
    login: 'Kirish', logout: 'Chiqish',
    pill_delivery: 'Tezkor yetkazish — 30 daqiqa',
    h_t1: 'MAZALI VA', h_t2: 'SIFATLI', h_t3: 'OVQATLAR',
    h_des: "Eng sara ichimliklar va fastfood mahsulotlari bir joyda. 60+ mahsulot, tezkor yetkazib berish, premium xizmat.",
    h_order: 'Hozir buyurtma ber', h_view_cart: "Savatni ko'r",
    cart: 'Savat', empty_cart: "Savat bo'sh", total: 'Jami',
    order_now: 'BUYURTMA BERISH'
  },
  ru: {
    nav_features: 'Преимущества', nav_contact: 'Контакты',
    login: 'Войти', logout: 'Выйти',
    pill_delivery: 'Быстрая доставка — 30 минут',
    h_t1: 'ВКУСНАЯ И', h_t2: 'КАЧЕСТВЕННАЯ', h_t3: 'ЕДА',
    h_des: 'Лучшие напитки и фастфуд в одном месте. 60+ товаров, быстрая доставка, премиум сервис.',
    h_order: 'Заказать сейчас', h_view_cart: 'Корзина',
    cart: 'Корзина', empty_cart: 'Корзина пуста', total: 'Итого',
    order_now: 'ОФОРМИТЬ ЗАКАЗ'
  },
  en: {
    nav_features: 'Features', nav_contact: 'Contact',
    login: 'Login', logout: 'Logout',
    pill_delivery: 'Fast delivery — 30 min',
    h_t1: 'TASTY AND', h_t2: 'QUALITY', h_t3: 'FOOD',
    h_des: 'Premium drinks and fast food in one place. 60+ products, fast delivery, premium service.',
    h_order: 'Order now', h_view_cart: 'View cart',
    cart: 'Cart', empty_cart: 'Cart is empty', total: 'Total',
    order_now: 'PLACE ORDER'
  }
};

let LANG = localStorage.getItem('qm_lang') || 'uz';
let THEME = localStorage.getItem('qm_theme') || 'dark';

function applyLang() {
  document.querySelectorAll('[data-tr]').forEach(el => {
    const k = el.getAttribute('data-tr');
    if (T[LANG] && T[LANG][k]) el.textContent = T[LANG][k];
  });
  document.querySelectorAll('.lb').forEach(b => b.classList.toggle('active', b.textContent.trim().toLowerCase() === LANG));
}

function setLang(l) {
  LANG = l;
  localStorage.setItem('qm_lang', l);
  applyLang();
  showToast('🌐', `${l.toUpperCase()} tanlandi`);
}

function applyTheme() {
  document.documentElement.setAttribute('data-theme', THEME);
  const btn = document.getElementById('themeBtn');
  if (btn) btn.textContent = THEME === 'dark' ? '🌙' : '☀️';
}

function toggleTheme() {
  THEME = THEME === 'dark' ? 'light' : 'dark';
  localStorage.setItem('qm_theme', THEME);
  applyTheme();
}

// === Sidebar ===
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('collapsed');
}

function showMain() {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  const msc = document.getElementById('msc');
  if (msc) msc.style.display = '';
  document.querySelectorAll('.si').forEach(b => b.classList.remove('active'));
  if (event && event.target) event.target.closest('.si')?.classList.add('active');
}

function showPanel(name) {
  const msc = document.getElementById('msc');
  if (msc) msc.style.display = 'none';
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  const panel = document.getElementById(`panel-${name}`);
  if (panel) panel.classList.add('active');
  document.querySelectorAll('.si').forEach(b => b.classList.remove('active'));
  if (event && event.target) event.target.closest('.si')?.classList.add('active');
  if (name === 'table') loadOrders();
  if (name === 'activity') loadLoginActivity();
  if (name === 'addprod') renderProductsAdmin();
}

// === Products ===
let PRODUCTS = window.__PRODUCTS__ || [];
let LIKED_IDS = new Set(window.__LIKED_IDS__ || []);
let currentTab = 'fastfood';

function categoryMeta(cat) {
  const map = {
    fastfood: { ico: '🍔', tit: 'FastFood', sub: 'Eng mazali tez taomlar' },
    drinks: { ico: '🥤', tit: 'Ichimliklar', sub: 'Salqin va sifatli ichimliklar' },
    milliy: { ico: '🍲', tit: 'Milliy taomlar', sub: "O'zbek milliy taomlari" },
    shirinliklar: { ico: '🍰', tit: 'Shirinliklar', sub: 'Mazali shirinliklar' },
    favorites: { ico: '❤️', tit: 'Yoqtirganlarim', sub: "Siz yoqtirgan mahsulotlar" },
    all: { ico: '⚡', tit: 'Barcha mahsulotlar', sub: 'Hammasi bir joyda' }
  };
  return map[cat] || map.all;
}

function renderProducts() {
  const grid = document.getElementById('pgrid');
  if (!grid) return;
  const list = currentTab === 'all'
    ? PRODUCTS
    : currentTab === 'favorites'
      ? PRODUCTS.filter(p => LIKED_IDS.has(p.id))
      : PRODUCTS.filter(p => p.category === currentTab);
  grid.innerHTML = list.map(p => `
    <div class="pcard" data-id="${p.id}">
      ${p.badge ? `<span class="pbadge ${p.badge}">${p.badge.toUpperCase()}</span>` : ''}
      <div class="pem">${p.emoji || '🍽️'}</div>
      <div class="pnm">${p.name}</div>
      <div class="pds">${p.description || ''}</div>
      <div class="prow">
        <div class="ppr">${formatPrice(p.price)} so'm</div>
        <button class="padd" onclick="addToCart(${p.id})"><i class="fas fa-plus"></i> Qo'shish</button>
      </div>
      <div class="prow" style="margin-top:8px">
        <div class="plimit">📦 ${Math.min((CART.find(i => i.id === p.id)?.qty || 1), 15)} / 15</div>
        <button class="padd" onclick="toggleFavorite(${p.id})">${LIKED_IDS.has(p.id) ? '❤️' : '🤍'}</button>
      </div>
    </div>
  `).join('') || `<div class="cart-empty"><div class="em">📦</div>Mahsulotlar topilmadi</div>`;

  const sectit = document.getElementById('sectit');
  const secsub = document.getElementById('secsub');
  const secico = document.getElementById('secico');
  const seccnt = document.getElementById('seccnt');
  if (sectit) sectit.textContent = categoryMeta(currentTab).tit;
  if (secsub) secsub.textContent = categoryMeta(currentTab).sub;
  if (secico) secico.textContent = categoryMeta(currentTab).ico;
  if (seccnt) seccnt.textContent = `${list.length} ta mahsulot`;
  updateCounts();
}

function updateCounts() {
  const counts = { fastfood: 0, drinks: 0, milliy: 0, shirinliklar: 0, favorites: LIKED_IDS.size, all: PRODUCTS.length };
  PRODUCTS.forEach(p => { if (counts[p.category] !== undefined) counts[p.category]++; });
  const ids = { fastfood: 'c-ff', drinks: 'c-dr', milliy: 'c-mi', shirinliklar: 'c-sh', favorites: 'c-fv', all: 'c-al' };
  Object.keys(ids).forEach(k => { const el = document.getElementById(ids[k]); if (el) el.textContent = counts[k]; });
}

function switchTab(tab, evt) {
  currentTab = tab;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  const tabIds = { fastfood: 't-ff', drinks: 't-dr', milliy: 't-mi', shirinliklar: 't-sh', favorites: 't-fv', all: 't-al' };
  const el = document.getElementById(tabIds[tab]); if (el) el.classList.add('active');
  renderProducts();
}

async function toggleFavorite(productId) {
  const isAuthed = !!document.getElementById('userArea');
  if (!isAuthed) {
    showToast('🔐', "Yoqtirish uchun avval kiring");
    return openAuth();
  }
  const r = await api(`/products/api/favorites/${productId}/toggle/`, { method: 'POST' });
  if (!(r.ok && r.data.ok)) {
    showToast('❌', 'Yoqtirganlar yangilanmadi');
    return;
  }
  if (r.data.liked) LIKED_IDS.add(productId);
  else LIKED_IDS.delete(productId);
  renderProducts();
  showToast('❤️', r.data.liked ? "Yoqtirganlarga qo'shildi" : "Yoqtirganlardan olindi");
}

function renderFeatured() {
  const list = document.getElementById('featList');
  if (!list) return;
  const featured = PRODUCTS.filter(p => p.badge === 'hot' || p.badge === 'new').slice(0, 4);
  list.innerHTML = featured.map(p => `
    <div class="fil-i" onclick="addToCart(${p.id})" style="cursor:pointer">
      <div class="fil-em">${p.emoji}</div>
      <div style="flex:1">
        <div class="fil-tt">${p.name}</div>
        <div class="fil-pr">${formatPrice(p.price)} so'm</div>
      </div>
    </div>
  `).join('');
}

function formatPrice(n) {
  return new Intl.NumberFormat('en-US').format(n).replace(/,/g, ' ');
}

// === Search ===
function doSearch(q) {
  const res = document.getElementById('sres');
  q = q.trim().toLowerCase();
  if (!q) { res.classList.remove('open'); return; }
  const matches = PRODUCTS.filter(p =>
    p.name.toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q)
  ).slice(0, 8);
  res.innerHTML = matches.map(p => `
    <div class="sres-i" onclick="addToCart(${p.id});document.getElementById('sres').classList.remove('open')">
      <div style="font-size:1.5rem">${p.emoji}</div>
      <div style="flex:1">
        <div style="font-weight:700;font-size:.85rem">${p.name}</div>
        <div style="color:var(--orange);font-size:.75rem;font-family:'JetBrains Mono',monospace">${formatPrice(p.price)} so'm</div>
      </div>
    </div>
  `).join('') || '<div style="padding:14px;color:var(--t3);font-size:.85rem;text-align:center">Hech narsa topilmadi</div>';
  res.classList.add('open');
}

// === Cart with limits 1-15 ===
const CART_MIN = 1;
const CART_MAX = 15;
let CART = JSON.parse(localStorage.getItem('qm_cart') || '[]');

function saveCart() {
  localStorage.setItem('qm_cart', JSON.stringify(CART));
  updateBadges();
  renderCart();
}

function updateBadges() {
  const total = CART.reduce((s, i) => s + i.qty, 0);
  ['hbadge', 'fbadge'].forEach(id => { const el = document.getElementById(id); if (el) el.textContent = total; });
}

function addToCart(id) {
  const product = PRODUCTS.find(p => p.id === id);
  if (!product) return;
  const existing = CART.find(c => c.id === id);
  if (existing) {
    if (existing.qty >= CART_MAX) {
      showToast('⚠️', `Maksimum ${CART_MAX} ta qo'shish mumkin`);
      return;
    }
    existing.qty++;
  } else {
    CART.push({ id, name: product.name, emoji: product.emoji, price: product.price, qty: 1 });
  }
  saveCart();
  showToast('🛒', `${product.name} savatga qo'shildi`);
}

function removeFromCart(id) {
  CART = CART.filter(c => c.id !== id);
  saveCart();
}

function changeQty(id, delta) {
  const item = CART.find(c => c.id === id);
  if (!item) return;
  const newQty = item.qty + delta;
  if (newQty < CART_MIN) {
    removeFromCart(id);
    return;
  }
  if (newQty > CART_MAX) {
    showToast('⚠️', `Maksimum ${CART_MAX} ta`);
    return;
  }
  item.qty = newQty;
  saveCart();
}

let appliedPromo = null;

function renderCart() {
  const body = document.getElementById('cartBd');
  const ft = document.getElementById('cartFt');
  if (!body) return;
  if (CART.length === 0) {
    body.innerHTML = `<div class="cart-empty"><div class="em">🛒</div>Savatingiz bo'sh</div>`;
    if (ft) ft.style.display = 'none';
    return;
  }
  body.innerHTML = CART.map(i => `
    <div class="ci">
      <div class="ci-em">${i.emoji}</div>
      <div class="ci-info">
        <div class="ci-nm">${i.name}</div>
        <div class="ci-pr">${formatPrice(i.price)} so'm</div>
        <div class="ci-act">
          <button class="ci-btn" onclick="changeQty(${i.id},-1)" ${i.qty <= CART_MIN ? 'disabled' : ''}>−</button>
          <span class="ci-qty">${i.qty}</span>
          <button class="ci-btn" onclick="changeQty(${i.id},1)" ${i.qty >= CART_MAX ? 'disabled' : ''}>+</button>
        </div>
        <div style="font-size:.65rem;color:var(--t3);margin-top:4px">Limit: ${CART_MIN}-${CART_MAX}</div>
      </div>
      <button class="ci-rm" onclick="removeFromCart(${i.id})"><i class="fas fa-trash"></i></button>
    </div>
  `).join('');
  if (ft) ft.style.display = '';
  let total = CART.reduce((s, i) => s + i.price * i.qty, 0);
  let discountAmt = 0;
  if (appliedPromo && total >= 100000) discountAmt = Math.round(total * 0.2);
  const cartTot = document.getElementById('cartTot');
  if (cartTot) cartTot.textContent = `${formatPrice(total - discountAmt)} so'm`;
  const drow = document.getElementById('discountRow');
  const damt = document.getElementById('discountAmt');
  if (discountAmt > 0 && drow) { drow.style.display = ''; if (damt) damt.textContent = `−${formatPrice(discountAmt)} so'm`; }
  else if (drow) drow.style.display = 'none';
}

function openCart() {
  const ov = document.getElementById('cartOv');
  const sb = document.getElementById('cartSb');
  if (ov) ov.classList.add('open');
  if (sb) sb.classList.add('open');
  renderCart();
}
function closeCart() {
  const ov = document.getElementById('cartOv');
  const sb = document.getElementById('cartSb');
  if (ov) ov.classList.remove('open');
  if (sb) sb.classList.remove('open');
}

function applyPromo() {
  const inp = document.getElementById('promoInp');
  const code = (inp?.value || '').trim().toUpperCase();
  const total = CART.reduce((s, i) => s + i.price * i.qty, 0);
  if (total < 100000) { showToast('⚠️', "100 000 so'mdan ortiq haridda ishlaydi"); return; }
  if (code === 'QUVVAT20' || code === 'QM20') {
    appliedPromo = code;
    const promoOk = document.getElementById('promoOk');
    const promoOkTxt = document.getElementById('promoOkTxt');
    if (promoOk) promoOk.style.display = '';
    if (promoOkTxt) promoOkTxt.textContent = `${code} qo'llanildi (−20%)`;
    renderCart();
    showToast('✅', "20% chegirma qo'llandi");
  } else {
    showToast('❌', "Noto'g'ri promo kod");
  }
}

// === Toast ===
let toastTimer;
function showToast(icon, txt) {
  const t = document.getElementById('toast');
  const tIcon = document.getElementById('tIcon');
  const tTxt = document.getElementById('tTxt');
  if (tIcon) tIcon.textContent = icon;
  if (tTxt) tTxt.textContent = txt;
  if (t) t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { if (t) t.classList.remove('show'); }, 2800);
}

// === Auth ===
function openAuth() { document.getElementById('authModal')?.classList.add('open'); }
function closeAuth() { document.getElementById('authModal')?.classList.remove('open'); }

function switchAuth(mode) {
  ['login', 'reg', 'admin'].forEach(m => {
    const tab = document.getElementById(`atab-${m}`);
    const sec = document.getElementById(`as-${m}`);
    if (tab) tab.classList.toggle('active', m === mode);
    if (sec) sec.style.display = m === mode ? '' : 'none';
  });
}

async function doLogin() {
  const username = document.getElementById('lu')?.value.trim();
  const password = document.getElementById('lp')?.value;
  if (!username || !password) return showToast('⚠️', "Maydonlarni to'ldiring");
  const r = await api('/accounts/api/login/', { method: 'POST', body: JSON.stringify({ username, password }) });
  if (r.ok && r.data.ok) {
    showToast('✅', 'Muvaffaqiyatli kirdingiz');
    setTimeout(() => location.reload(), 800);
  } else {
    showToast('❌', r.data.error || 'Login yoki parol xato');
  }
}

async function doRegister() {
  const data = {
    first_name: document.getElementById('rn')?.value.trim() || 'Sherjonov',
    last_name: document.getElementById('rs')?.value.trim() || 'Abduaziz',
    username: document.getElementById('ru')?.value.trim(),
    email: document.getElementById('re')?.value.trim(),
    phone: (document.getElementById('rph')?.value || '').replace(/\D/g, ''),
    password: document.getElementById('rp')?.value,
  };
  if (!data.first_name || !data.username || !data.email || !data.password) {
    return showToast('⚠️', "Barcha maydonlarni to'ldiring");
  }
  if (data.phone && !/^\d{7,15}$/.test(data.phone)) {
    return showToast('⚠️', "Telefon faqat raqamlardan iborat bo'lsin");
  }
  const r = await api('/accounts/api/register/', { method: 'POST', body: JSON.stringify(data) });
  if (r.ok && r.data.ok) {
    const step = document.getElementById('regOtpStep');
    if (step) step.style.display = '';
    buildOtp('regOtpWrap', 6);
    // Auto-fill the OTP code
    if (r.data.code) {
      autoFillOtp('regOtpWrap', r.data.code);
    }
    showToast('📬', 'Kod emailga yuborildi va avtoto`ldirildi');
  } else {
    showToast('❌', r.data.error || "Ro'yxatdan o'tish xatosi");
  }
}

async function confirmReg() {
  const code = collectOtp('regOtpWrap');
  const email = document.getElementById('re')?.value.trim();
  const r = await api('/accounts/api/verify-otp/', { method: 'POST', body: JSON.stringify({ email, code, action: 'register' }) });
  if (r.ok && r.data.ok) {
    showToast('✅', 'Akkount tasdiqlandi');
    setTimeout(() => location.reload(), 800);
  } else {
    showToast('❌', r.data.error || "Kod noto'g'ri");
  }
}

async function doAdmin() {
  const username = document.getElementById('au')?.value.trim();
  const password = document.getElementById('ap')?.value;
  const r = await api('/accounts/api/login/', { method: 'POST', body: JSON.stringify({ username, password }) });
  if (r.ok && r.data.ok && r.data.is_admin) {
    showToast('✅', 'Admin sifatida kirdingiz');
    setTimeout(() => location.reload(), 800);
  } else {
    showToast('❌', r.data.error || 'Admin emas yoki parol xato');
  }
}

async function logout() {
  await api('/accounts/api/logout/', { method: 'POST' });
  location.reload();
}

function toggleUD() { document.getElementById('udrop')?.classList.toggle('open'); }

function buildOtp(wrapId, len) {
  const wrap = document.getElementById(wrapId);
  if (!wrap) return;
  wrap.innerHTML = '';
  for (let i = 0; i < len; i++) {
    const inp = document.createElement('input');
    inp.className = 'otp-i'; inp.maxLength = 1; inp.dataset.idx = i;
    inp.addEventListener('input', e => {
      const next = wrap.querySelector(`[data-idx="${i + 1}"]`);
      if (e.target.value && next) next.focus();
    });
    inp.addEventListener('keydown', e => {
      if (e.key === 'Backspace' && !e.target.value) {
        const prev = wrap.querySelector(`[data-idx="${i - 1}"]`);
        if (prev) prev.focus();
      }
    });
    wrap.appendChild(inp);
  }
}

function autoFillOtp(wrapId, code) {
  const wrap = document.getElementById(wrapId);
  if (!wrap || !code) return;
  const inputs = wrap.querySelectorAll('.otp-i');
  const codeStr = String(code);
  inputs.forEach((inp, idx) => {
    if (codeStr[idx]) inp.value = codeStr[idx];
  });
}

function collectOtp(wrapId) {
  const wrap = document.getElementById(wrapId);
  if (!wrap) return '';
  return Array.from(wrap.querySelectorAll('.otp-i')).map(i => i.value).join('');
}

// === Address: Viloyat -> Tuman -> Mahalla ===
const DISTRICTS = {
  "Toshkent shahar": ["Bektemir", "Chilanzar", "Mirzo Ulug'bek", "Mirobod", "Olmazor", "Sergeli", "Shayhontohur", "Uchtepa", "Yakkasaroy", "Yunusobod", "Yashnobod"],
  "Toshkent viloyati": ["Angren", "Olmaliq", "Chirchiq", "Bekobod", "Oqqo'rg'on", "Bo'stonliq", "Zangiota", "Qibray", "Parkent"],
  "Samarqand viloyati": ["Samarqand shahar", "Urgut", "Jomboy", "Kattaqo'rg'on", "Payariq", "Bulungur", "Oqdaryo", "Ishtixon"],
  "Buxoro viloyati": ["Buxoro shahar", "G'ijduvon", "Kogon", "Vobkent", "Olot", "Qorako'l", "Jondor", "Romitan"],
  "Andijon viloyati": ["Andijon shahar", "Asaka", "Xonobod", "Qo'rg'ontepa", "Baliqchi", "Bo'z", "Ulug'nor", "Marxamat"],
  "Farg'ona viloyati": ["Farg'ona shahar", "Marg'ilon", "Quva", "Qo'qon", "Rishton", "Beshariq", "Bog'dod", "Oltiariq"],
  "Namangan viloyati": ["Namangan shahar", "Chortoq", "Pop", "Uchqo'rg'on", "Chust", "Kosonsoy", "Mingbuloq", "Norin"],
  "Qashqadaryo viloyati": ["Qarshi shahar", "Shahrisabz", "Kitob", "Koson", "G'uzor", "Chiroqchi", "Muborak", "Nishon"],
  "Surxondaryo viloyati": ["Termiz shahar", "Denov", "Sherobod", "Boysun", "Sho'rchi", "Jarqo'rg'on", "Qumqo'rg'on", "Oltinsoy"],
  "Xorazm viloyati": ["Urganch shahar", "Xiva shahar", "Xiva tumani", "Bog'ot", "Gurlan", "Xonqa", "Hazorasp", "Shovot", "Yangibozor", "Yangiariq", "Qo'shko'pir"],
  "Navoiy viloyati": ["Navoiy shahar", "Zarafshon", "Nurota", "Karmana", "Qiziltepa", "Xatirchi", "Uchquduq", "Tomdi"],
  "Qoraqalpog'iston": ["Nukus shahar", "Xo'jayli", "Qo'ng'irot", "Beruniy", "Qorao'zak", "Chimboy", "Kegeyli", "Muynoq"]
};

const MAHALLAS = {
  "Xiva shahar": ["Badirxon", "Yangi obod", "Do'stlik", "Mustaqillik", "Navoiy", "Ipak yo'li", "Mehnat", "Bog' ko'cha", "Guliston", "Tinchlik"],
  "Xiva tumani": ["Shovot qishlog'i", "Yangibozor qishlog'i", "Oqmachit", "Ko'hna Urganch", "Qorako'l", "Darvoza"],
  "Urganch shahar": ["Yoshlik", "Al-Xorazmiy", "Farobiy", "Do'stlik", "Markaziy", "Yangi turmush", "Bog'", "Navoiy ko'chasi"],
  // Default fallback mahallas
  "default": ["Markaziy", "Yangi turmush", "Do'stlik", "Tinchlik", "Mustaqillik", "Navoiy", "Mehnat", "Yoshlik", "Guliston", "Bog'"]
};

function updateDistricts() {
  const reg = document.getElementById('oReg')?.value;
  const districtWrap = document.getElementById('districtWrap');
  const districtSel = document.getElementById('oDistrict');
  const mahallaWrap = document.getElementById('mahallaWrap');
  const houseWrap = document.getElementById('houseWrap');
  
  if (!reg) {
    if (districtWrap) districtWrap.style.display = 'none';
    if (mahallaWrap) mahallaWrap.style.display = 'none';
    if (houseWrap) houseWrap.style.display = 'none';
    updateDel();
    return;
  }
  
  const districts = DISTRICTS[reg] || [];
  if (districtSel) {
    districtSel.innerHTML = '<option value="">— Tuman tanlang —</option>' + 
      districts.map(d => `<option value="${d}">${d}</option>`).join('');
  }
  if (districtWrap) districtWrap.style.display = '';
  if (mahallaWrap) mahallaWrap.style.display = 'none';
  if (houseWrap) houseWrap.style.display = 'none';
  updateDel();
}

function updateMahallas() {
  const district = document.getElementById('oDistrict')?.value;
  const mahallaWrap = document.getElementById('mahallaWrap');
  const mahallaSel = document.getElementById('oMahalla');
  const houseWrap = document.getElementById('houseWrap');
  
  if (!district) {
    if (mahallaWrap) mahallaWrap.style.display = 'none';
    if (houseWrap) houseWrap.style.display = 'none';
    return;
  }
  
  const mahallas = MAHALLAS[district] || MAHALLAS["default"];
  if (mahallaSel) {
    mahallaSel.innerHTML = '<option value="">— Mahalla tanlang —</option>' + 
      mahallas.map(m => `<option value="${m}">${m}</option>`).join('');
  }
  if (mahallaWrap) mahallaWrap.style.display = '';
  if (houseWrap) houseWrap.style.display = '';
}

function updateDel() {
  const reg = document.getElementById('oReg')?.value;
  const dtxt = document.getElementById('dtxt');
  if (!dtxt) return;
  if (!reg) { dtxt.textContent = 'Viloyatni tanlang'; return; }
  const tashkent = ['Toshkent shahar', 'Toshkent viloyati'];
  dtxt.textContent = tashkent.includes(reg) ? '🚚 30 daqiqa, bepul yetkazish' : "🚚 2 soat ichida, 30 000 so'm";
}

// === Order ===
let selPayMethod = 'cash';

function selPay(m) {
  selPayMethod = m;
  document.querySelectorAll('.pm').forEach(el => el.classList.remove('sel'));
  const pm = document.getElementById(`pm-${m}`);
  if (pm) pm.classList.add('sel');
  const cf = document.getElementById('cfields');
  if (cf) cf.classList.toggle('open', m === 'card');
  const opi = document.getElementById('opinfo');
  const opitxt = document.getElementById('opitxt');
  if (m === 'click') { if (opi) opi.style.display = ''; if (opitxt) opitxt.textContent = "Click ilovasiga yo'naltirilasiz"; }
  else if (m === 'payme') { if (opi) opi.style.display = ''; if (opitxt) opitxt.textContent = "Payme ilovasiga yo'naltirilasiz"; }
  else if (opi) opi.style.display = 'none';
}

function openOrder() {
  if (CART.length === 0) return showToast('⚠️', "Savat bo'sh");
  closeCart();
  document.getElementById('orderModal')?.classList.add('open');
  const recap = document.getElementById('oRecap');
  if (recap) {
    recap.innerHTML = CART.map(i => `<div class="rci"><span>${i.emoji} ${i.name} × ${i.qty}</span><span style="color:var(--orange);font-family:'JetBrains Mono',monospace">${formatPrice(i.price * i.qty)}</span></div>`).join('');
  }
}

function closeOrder() { document.getElementById('orderModal')?.classList.remove('open'); }

function fmtCard(el) {
  el.value = el.value.replace(/\D/g, '').replace(/(.{4})/g, '$1 ').trim().slice(0, 19);
  const raw = el.value.replace(/\s/g, '');
  const cvNum = document.getElementById('cvNum');
  if (cvNum) cvNum.textContent = el.value || '•••• •••• •••• ••••';
  const cardTypeInfo = document.getElementById('cardTypeInfo');
  if (cardTypeInfo) {
    let type = 'Aniqlanmadi';
    if (raw.startsWith('4700') || raw.startsWith('4')) type = 'Visa';
    else if (raw.startsWith('5')) type = 'MasterCard';
    else if (raw.startsWith('9860')) type = 'Uzcard';
    else if (raw.startsWith('8600')) type = 'Humo';
    cardTypeInfo.textContent = `Karta turi: ${type}`;
  }
}

function fmtExp(el) {
  let v = el.value.replace(/\D/g, '');
  if (v.length >= 2) v = v.slice(0, 2) + ' / ' + v.slice(2, 4);
  el.value = v;
  const cvExp = document.getElementById('cvExp');
  if (cvExp) cvExp.textContent = v || 'MM/YY';
}

async function submitOrder() {
  const passSeries = (document.getElementById('passportSeries')?.value || '').toUpperCase().replace(/[^A-Z]/g, '').slice(0, 2);
  const passNumber = (document.getElementById('passportNumber')?.value || '').replace(/\D/g, '').slice(0, 7);
  const passPinfl = (document.getElementById('passportPinfl')?.value || '').replace(/\D/g, '').slice(0, 14);
  const passOk = /^[A-Z]{2}$/.test(passSeries) && /^\d{7}$/.test(passNumber) && /^\d{14}$/.test(passPinfl);
  const pInfo = document.getElementById('passportInfo');
  if (pInfo) pInfo.textContent = passOk ? '✅ 16 yan tasdiqlandi' : '❌ Passport ma`lumotlarini tekshiring';

  const data = {
    first_name: document.getElementById('oNm')?.value.trim(),
    last_name: document.getElementById('oSn')?.value.trim(),
    phone: (document.getElementById('oPh')?.value || '').replace(/\D/g, ''),
    email: document.getElementById('oEm')?.value.trim(),
    region: document.getElementById('oReg')?.value,
    district: document.getElementById('oDistrict')?.value || '',
    mahalla: document.getElementById('oMahalla')?.value || '',
    house: document.getElementById('oHouse')?.value || '',
    payment_method: selPayMethod,
    card_number: (document.getElementById('cnum')?.value || '').replace(/\D/g, ''),
    passport_series: passSeries,
    passport_number: passNumber,
    passport_pinfl: passPinfl,
    promo_code: appliedPromo,
    items: CART
  };
  if (!data.first_name || !data.phone || !data.region) return showToast('⚠️', "Barcha maydonlarni to'ldiring");
  if (!/^\d{7,15}$/.test(data.phone)) return showToast('⚠️', 'Telefon faqat raqam bo`lsin');
  if (!passOk) return showToast('⚠️', 'Passport/JSHSHIR noto`g`ri');
  const r = await api('/orders/api/create/', { method: 'POST', body: JSON.stringify(data) });
  if (r.ok && r.data.ok) {
    closeOrder();
    const soid = document.getElementById('soid');
    if (soid) soid.textContent = `#${r.data.order_number}`;
    document.getElementById('succ')?.classList.add('open');
    CART = []; appliedPromo = null; saveCart();
  } else {
    showToast('❌', r.data.error || 'Buyurtma xatosi');
  }
}

function fillAllLimits() {
  if (CART.length === 0) return showToast('⚠️', "Savat bo'sh");
  if (!confirm("Hamma mahsulotlarni 15 taga to'ldiramizmi?")) return;
  if (!confirm("Shaxsingizni tasdiqlang")) return;
  CART = CART.map(i => ({ ...i, qty: 15 }));
  saveCart();
  renderProducts();
  showToast('✅', 'Barcha limitlar 15 ga to`ldirildi');
}

function closeSucc() { document.getElementById('succ')?.classList.remove('open'); }

// === Contact form ===
async function sendContact() {
  const data = {
    name: document.getElementById('cfn')?.value.trim(),
    phone: document.getElementById('cfp')?.value.trim(),
    email: document.getElementById('cfe')?.value.trim(),
    message: document.getElementById('cfm')?.value.trim()
  };
  if (!data.name || !data.message) return showToast('⚠️', "Maydonlarni to'ldiring");
  showToast('✅', 'Xabaringiz yuborildi');
  ['cfn', 'cfp', 'cfe', 'cfm'].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
}

// === Admin: Load orders ===
async function loadOrders() {
  const panel = document.getElementById('panel-table');
  if (!panel) return;
  const r = await api('/orders/api/list/');
  if (!r.ok) {
    panel.innerHTML = '<p style="color:var(--t3);text-align:center;padding:40px">Buyurtmalar topilmadi</p>';
    return;
  }
  const orders = r.data.orders || [];
  if (orders.length === 0) {
    panel.innerHTML = '<p style="color:var(--t3);text-align:center;padding:40px">Buyurtmalar yo\'q</p>';
    return;
  }
  panel.innerHTML = `
    <div style="padding:20px">
      <h3 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:16px">📦 Buyurtmalar tarixi</h3>
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Mijoz</th>
              <th>Telefon</th>
              <th>Mahsulotlar</th>
              <th>Jami</th>
              <th>Sana</th>
              <th>Holat</th>
            </tr>
          </thead>
          <tbody>
            ${orders.map((o, idx) => `
              <tr>
                <td>${idx + 1}</td>
                <td><strong>${o.customer_name}</strong></td>
                <td>${o.phone}</td>
                <td>${o.items_summary || '-'}</td>
                <td style="color:var(--orange);font-family:'JetBrains Mono',monospace">${formatPrice(o.total)} so'm</td>
                <td>${o.created_at}</td>
                <td><span class="status-badge status-${o.status}">${o.status_display}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// === Admin: Load Login Activity ===
async function loadLoginActivity() {
  const panel = document.getElementById('panel-activity');
  if (!panel) return;
  const r = await api('/accounts/api/login-activity/');
  if (!r.ok) {
    panel.innerHTML = '<p style="color:var(--t3);text-align:center;padding:40px">Ma\'lumot topilmadi</p>';
    return;
  }
  const activities = r.data.activities || [];
  if (activities.length === 0) {
    panel.innerHTML = '<p style="color:var(--t3);text-align:center;padding:40px">Faollik yo\'q</p>';
    return;
  }
  panel.innerHTML = `
    <div style="padding:20px">
      <h3 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:16px">👥 Kirish/Chiqish jadvali</h3>
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Ism Familiya</th>
              <th>Username</th>
              <th>Harakat</th>
              <th>Sana va vaqt</th>
              <th>IP</th>
            </tr>
          </thead>
          <tbody>
            ${activities.map((a, idx) => `
              <tr>
                <td>${idx + 1}</td>
                <td><strong>${a.full_name || '-'}</strong></td>
                <td>${a.username || '-'}</td>
                <td><span class="action-badge action-${a.action}">${a.action_display}</span></td>
                <td>${a.created_at}</td>
                <td style="font-family:'JetBrains Mono',monospace;font-size:.75rem">${a.ip || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// === Admin: Render Products ===
function renderProductsAdmin() {
  const panel = document.getElementById('panel-addprod');
  if (!panel) return;
  panel.innerHTML = `
    <div style="padding:20px">
      <h3 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:16px">📦 Mahsulotlar boshqaruvi</h3>
      <div style="margin-bottom:20px">
        <button class="btnp" onclick="openAddProduct()"><i class="fas fa-plus"></i> Yangi mahsulot qo'shish</button>
      </div>
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Emoji</th>
              <th>Nomi</th>
              <th>Kategoriya</th>
              <th>Narx</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            ${PRODUCTS.map((p, idx) => `
              <tr>
                <td>${idx + 1}</td>
                <td style="font-size:1.5rem">${p.emoji}</td>
                <td><strong>${p.name}</strong></td>
                <td>${p.category_name || p.category}</td>
                <td style="color:var(--orange);font-family:'JetBrains Mono',monospace">${formatPrice(p.price)} so'm</td>
                <td>
                  <button class="btn-small" onclick="editProduct(${p.id})"><i class="fas fa-edit"></i></button>
                  <button class="btn-small btn-danger" onclick="deleteProduct(${p.id})"><i class="fas fa-trash"></i></button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function openAddProduct() {
  showToast('🔧', 'Mahsulot qo\'shish funksiyasi');
}

function editProduct(id) {
  showToast('🔧', `Mahsulot #${id} tahrirlash`);
}

async function deleteProduct(id) {
  if (!confirm('Mahsulotni o\'chirmoqchimisiz?')) return;
  const r = await api(`/products/api/delete/${id}/`, { method: 'POST' });
  if (r.ok) {
    showToast('✅', 'Mahsulot o\'chirildi');
    PRODUCTS = PRODUCTS.filter(p => p.id !== id);
    renderProductsAdmin();
    renderProducts();
  } else {
    showToast('❌', 'Xatolik yuz berdi');
  }
}

// === Init ===
document.addEventListener('DOMContentLoaded', () => {
  applyTheme();
  applyLang();
  renderProducts();
  renderFeatured();
  updateBadges();
  setTimeout(() => {
    const intro = document.getElementById('intro');
    if (intro) intro.classList.add('hide');
  }, 1600);
  
  // Close dropdowns on outside click
  document.addEventListener('click', (e) => {
    const udrop = document.getElementById('udrop');
    const uavbtn = document.getElementById('uavbtn');
    if (udrop && !udrop.contains(e.target) && e.target !== uavbtn) {
      udrop.classList.remove('open');
    }
  });
});
