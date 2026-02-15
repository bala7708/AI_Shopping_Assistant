#!/usr/bin/env python3
"""
AI Shopping Assistant — Custom AI (no external API needed)
Run:  python ai_shopping_app.py
Open: http://localhost:5000
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re

# ─────────────────────────────────────────────
# PRODUCT CATALOG
# ─────────────────────────────────────────────
PRODUCTS = [
    {"id": 1,  "name": "Wireless Headphones",     "price": 299.99, "category": "Electronics",   "rating": 4.8, "stock": 15, "image": "🎧", "tags": ["audio","music","sound","headphone","wireless"]},
    {"id": 2,  "name": "Ergonomic Office Chair",   "price": 449.00, "category": "Furniture",     "rating": 4.6, "stock": 8,  "image": "🪑", "tags": ["chair","office","seat","desk","furniture"]},
    {"id": 3,  "name": "Cold-Brew Coffee Kit",     "price": 34.99,  "category": "Food & Drink",  "rating": 4.9, "stock": 42, "image": "☕", "tags": ["coffee","brew","drink","caffeine","food"]},
    {"id": 4,  "name": "Smart Fitness Tracker",    "price": 129.95, "category": "Electronics",   "rating": 4.5, "stock": 30, "image": "⌚", "tags": ["fitness","tracker","watch","health","sport","exercise","gym"]},
    {"id": 5,  "name": "Premium Cork Yoga Mat",    "price": 78.00,  "category": "Sports",        "rating": 4.7, "stock": 20, "image": "🧘", "tags": ["yoga","mat","sport","exercise","fitness","gym"]},
    {"id": 6,  "name": "Mechanical Keyboard",      "price": 159.99, "category": "Electronics",   "rating": 4.9, "stock": 12, "image": "⌨️", "tags": ["keyboard","typing","computer","gaming","office","tech"]},
    {"id": 7,  "name": "Steel Water Bottle",       "price": 39.95,  "category": "Sports",        "rating": 4.8, "stock": 60, "image": "🍶", "tags": ["water","bottle","hydration","sport","outdoor"]},
    {"id": 8,  "name": "Succulent Garden Set",     "price": 29.99,  "category": "Home & Garden", "rating": 4.6, "stock": 25, "image": "🌵", "tags": ["plant","garden","succulent","home","decor","gift"]},
    {"id": 9,  "name": "Bluetooth Speaker",        "price": 89.99,  "category": "Electronics",   "rating": 4.7, "stock": 18, "image": "🔊", "tags": ["speaker","audio","bluetooth","music","sound","wireless"]},
    {"id": 10, "name": "Leather Journal",          "price": 24.99,  "category": "Stationery",    "rating": 4.8, "stock": 50, "image": "📔", "tags": ["journal","notebook","write","stationery","gift","diary"]},
    {"id": 11, "name": "Pour-Over Coffee Set",     "price": 55.00,  "category": "Food & Drink",  "rating": 4.7, "stock": 22, "image": "🫖", "tags": ["coffee","pour","drink","caffeine","kitchen","food"]},
    {"id": 12, "name": "Ultralight Running Shoes", "price": 119.99, "category": "Sports",        "rating": 4.6, "stock": 35, "image": "👟", "tags": ["shoes","running","sport","exercise","outdoor","fitness"]},
]

# ─────────────────────────────────────────────
# CUSTOM AI ENGINE
# ─────────────────────────────────────────────
def smart_response(msg: str, cart: list) -> tuple:
    """Returns (response_text, highlighted_product_ids)."""
    text  = msg.lower().strip()
    words = set(re.findall(r'\w+', text))

    def by_category(cat):
        return [p for p in PRODUCTS if p["category"].lower() == cat.lower()]

    def top_rated(n=4):
        return sorted(PRODUCTS, key=lambda p: p["rating"], reverse=True)[:n]

    def under_price(limit):
        return [p for p in PRODUCTS if p["price"] <= limit]

    def fmt(p):
        return f"{p['image']} **{p['name']}** — ${p['price']:.2f} (⭐{p['rating']})"

    def ids(lst):
        return [p["id"] for p in lst]

    def cart_summary():
        if not cart:
            return None, 0
        lines, total = [], 0
        for item in cart:
            p = next((x for x in PRODUCTS if x["id"] == item["product_id"]), None)
            if p:
                cost = p["price"] * item["qty"]
                total += cost
                lines.append(f"• {p['image']} {p['name']} x{item['qty']} = ${cost:.2f}")
        return lines, total

    # ── greetings ─────────────────────────────
    if words & {"hello", "hi", "hey", "howdy", "hiya", "yo", "sup"}:
        return (
            "Hey there! 👋 I'm **ShopBot**, your personal shopping assistant!\n"
            "Ask me to find products, suggest gifts, check your cart, or anything else. What are you looking for?",
            []
        )

    # ── cart ──────────────────────────────────
    if words & {"cart", "basket", "order", "checkout", "total", "purchase"}:
        lines, total = cart_summary()
        if not lines:
            return "Your cart is empty 🛒 — want me to suggest something?", []
        ship = "🎉 FREE" if total >= 75 else "$5.99"
        return (
            "Here's your cart 🛒:\n" + "\n".join(lines) +
            f"\n\n**Subtotal:** ${total:.2f} | **Shipping:** {ship}",
            [item["product_id"] for item in cart]
        )

    # ── shipping / returns ────────────────────
    if words & {"ship", "shipping", "delivery", "arrive", "how", "long"}:
        return (
            "📦 **Shipping info:**\n"
            "• Standard delivery: 2–3 business days\n"
            "• Free shipping on orders over $75\n"
            "• Flat rate $5.99 otherwise",
            []
        )

    if words & {"return", "refund", "exchange", "policy"}:
        return "We offer **30-day free returns** on all items — no questions asked! 📦", []

    # ── budget search ─────────────────────────
    budget = re.search(r'under\s*\$?(\d+)|budget.*?\$?(\d+)|\$?(\d+)\s*or\s*less', text)
    if budget:
        limit = float(next(x for x in budget.groups() if x))
        picks = under_price(limit)
        if picks:
            return (
                f"Great picks under ${limit:.0f} 💚:\n" + "\n".join(fmt(p) for p in picks[:5]),
                ids(picks[:5])
            )
        return f"Nothing under ${limit:.0f} right now — try a higher budget?", []

    # ── categories ────────────────────────────
    if words & {"electronic", "electronics", "tech", "gadget", "gadgets"}:
        picks = by_category("Electronics")
        return "Our Electronics lineup 🔌:\n" + "\n".join(fmt(p) for p in picks), ids(picks)

    if words & {"audio", "headphone", "headphones", "music", "listen", "sound"}:
        picks = [p for p in PRODUCTS if "audio" in p["tags"] or "music" in p["tags"]]
        return (
            "Perfect for music lovers 🎵:\n" + "\n".join(fmt(p) for p in picks) +
            "\n\nHeadphones for personal use, Speaker for sharing!",
            ids(picks)
        )

    if words & {"coffee", "brew", "caffeine", "drink", "tea"}:
        picks = by_category("Food & Drink")
        return (
            "Coffee lover? ☕\n" + "\n".join(fmt(p) for p in picks) +
            "\n\nBoth are bestsellers — Cold-Brew Kit is great for beginners!",
            ids(picks)
        )

    if words & {"sport", "sports", "fitness", "gym", "workout", "exercise", "yoga", "run", "running", "active"}:
        picks = by_category("Sports") + [p for p in PRODUCTS if p["id"] == 4]
        return "Stay active! 💪\n" + "\n".join(fmt(p) for p in picks), ids(picks)

    if words & {"office", "work", "desk", "chair", "keyboard", "typing"}:
        picks = [p for p in PRODUCTS if p["id"] in (2, 6)]
        return (
            "Perfect work-from-home combo 🏠:\n" + "\n".join(fmt(p) for p in picks),
            ids(picks)
        )

    if words & {"gift", "present", "gifts", "birthday", "anniversary", "surprise"}:
        picks = [p for p in PRODUCTS if p["id"] in (3, 7, 8, 10)]
        return (
            "Top gift ideas 🎁:\n" + "\n".join(fmt(p) for p in picks) +
            "\n\nAll under $40 and crowd favorites!",
            ids(picks)
        )

    if words & {"home", "garden", "plant", "decor", "succulent"}:
        picks = by_category("Home & Garden")
        return "Spruce up your space 🌿:\n" + "\n".join(fmt(p) for p in picks), ids(picks)

    if words & {"journal", "notebook", "write", "writing", "stationery", "diary"}:
        picks = by_category("Stationery")
        return "For the writers ✍️:\n" + "\n".join(fmt(p) for p in picks), ids(picks)

    # ── best / popular ────────────────────────
    if words & {"best", "top", "popular", "recommend", "trending", "favourite", "favorite"}:
        picks = top_rated(4)
        return "Top-rated products ⭐:\n" + "\n".join(fmt(p) for p in picks), ids(picks)

    # ── cheap / expensive ─────────────────────
    if words & {"cheap", "affordable", "budget", "inexpensive", "low"}:
        picks = sorted(PRODUCTS, key=lambda p: p["price"])[:4]
        return "Best value picks 💰:\n" + "\n".join(fmt(p) for p in picks), ids(picks)

    if words & {"premium", "luxury", "expensive", "quality"}:
        picks = sorted(PRODUCTS, key=lambda p: p["price"], reverse=True)[:3]
        return "Our premium picks 👑:\n" + "\n".join(fmt(p) for p in picks), ids(picks)

    # ── show all ──────────────────────────────
    if words & {"all", "everything", "show", "list", "catalog", "products"}:
        return "Everything we carry 🛍️:\n" + "\n".join(fmt(p) for p in PRODUCTS), ids(PRODUCTS)

    # ── tag fuzzy match ───────────────────────
    matched = [p for p in PRODUCTS if words & set(p["tags"])]
    if matched:
        return "Here's what I found 🔍:\n" + "\n".join(fmt(p) for p in matched[:4]), ids(matched[:4])

    # ── fallback ──────────────────────────────
    return (
        "Not sure about that — here's what I can do:\n"
        "• **Categories:** electronics, sports, coffee, office, home\n"
        "• **Budget:** 'under $50', 'cheap', 'premium'\n"
        "• **Discover:** 'best sellers', 'gift ideas', 'show all'\n"
        "• **Help:** 'my cart', 'shipping info', 'returns'",
        []
    )


# ─────────────────────────────────────────────
# HTML FRONTEND
# ─────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ShopAI</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{--ink:#111;--bg:#f4f0e8;--sage:#2d5a4b;--gold:#c9922a;--white:#fff;--mist:#e8ede9}
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--ink);min-height:100vh}

  nav{background:var(--ink);display:flex;align-items:center;justify-content:space-between;padding:0 1.5rem;height:58px;position:sticky;top:0;z-index:100}
  .logo{font-family:'Fraunces',serif;font-size:1.5rem;color:#f4f0e8}
  .logo span{color:var(--gold)}
  .cart-btn{background:var(--sage);color:#fff;border:none;cursor:pointer;padding:.4rem 1rem;border-radius:30px;font-size:.85rem;font-weight:600;display:flex;align-items:center;gap:.4rem}
  .cart-btn:hover{opacity:.85}
  .badge{background:var(--gold);color:var(--ink);border-radius:50%;width:18px;height:18px;font-size:.68rem;font-weight:700;display:flex;align-items:center;justify-content:center}

  .layout{display:grid;grid-template-columns:1fr 350px;max-width:1300px;margin:0 auto;min-height:calc(100vh - 58px)}

  .products{padding:1.5rem;border-right:1px solid rgba(0,0,0,.08)}
  .section-head{font-family:'Fraunces',serif;font-size:1.3rem;margin-bottom:1rem}
  .filters{display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:1.2rem}
  .f-btn{padding:.3rem .8rem;border-radius:20px;border:1.5px solid rgba(0,0,0,.15);background:transparent;font-size:.8rem;cursor:pointer;font-family:'DM Sans',sans-serif;transition:all .15s}
  .f-btn:hover,.f-btn.active{background:var(--sage);border-color:var(--sage);color:#fff}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.9rem}

  .card{background:var(--white);border-radius:14px;padding:1rem;box-shadow:0 2px 12px rgba(0,0,0,.07);border:2px solid transparent;transition:transform .2s,border-color .2s;position:relative;animation:up .3s ease}
  .card:hover{transform:translateY(-3px)}
  .card.hl{border-color:var(--gold);box-shadow:0 0 0 3px rgba(201,146,42,.2)}
  .card.hl::after{content:'AI Pick ✨';position:absolute;top:-9px;right:8px;background:var(--gold);color:var(--ink);font-size:.62rem;font-weight:700;padding:2px 7px;border-radius:20px}
  .emoji{font-size:2rem;display:block;margin-bottom:.5rem}
  .c-name{font-weight:600;font-size:.85rem;margin-bottom:.3rem;line-height:1.3}
  .c-meta{display:flex;justify-content:space-between;margin-bottom:.4rem}
  .c-price{font-weight:700;font-size:.95rem}
  .c-rating{font-size:.75rem;color:var(--gold)}
  .c-stock{font-size:.7rem;color:#888;margin-bottom:.6rem}
  .add{width:100%;background:var(--sage);color:#fff;border:none;cursor:pointer;padding:.4rem;border-radius:7px;font-size:.78rem;font-weight:500;font-family:'DM Sans',sans-serif}
  .add:hover{opacity:.85}

  .chat{display:flex;flex-direction:column;position:sticky;top:58px;height:calc(100vh - 58px);background:var(--white)}
  .chat-hd{background:var(--sage);color:#fff;padding:1rem 1.2rem;display:flex;align-items:center;gap:.7rem}
  .av{width:36px;height:36px;background:var(--gold);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem}
  .chat-hd h3{font-size:.9rem;font-weight:600}
  .online{font-size:.72rem;opacity:.7;display:flex;align-items:center;gap:4px}
  .dot{width:6px;height:6px;background:#6efcb0;border-radius:50%;animation:pulse 1.5s infinite}
  .msgs{flex:1;overflow-y:auto;padding:1rem;display:flex;flex-direction:column;gap:.7rem}
  .msgs::-webkit-scrollbar{width:3px}
  .msgs::-webkit-scrollbar-thumb{background:#ccc;border-radius:2px}
  .msg{max-width:88%;padding:.6rem .9rem;border-radius:12px;font-size:.84rem;line-height:1.5;animation:up .25s ease}
  .bot{background:var(--mist);align-self:flex-start;border-bottom-left-radius:3px}
  .usr{background:var(--sage);color:#fff;align-self:flex-end;border-bottom-right-radius:3px}
  .typing{background:var(--mist);align-self:flex-start;padding:.55rem .9rem}
  .dots{display:flex;gap:4px}
  .dots span{width:6px;height:6px;background:var(--sage);border-radius:50%;animation:bounce .8s infinite}
  .dots span:nth-child(2){animation-delay:.15s}
  .dots span:nth-child(3){animation-delay:.3s}
  .chips{padding:.5rem 1rem;display:flex;flex-wrap:wrap;gap:.35rem}
  .chip{background:var(--mist);border:1px solid rgba(0,0,0,.1);border-radius:20px;padding:.25rem .7rem;font-size:.74rem;cursor:pointer;font-family:'DM Sans',sans-serif;transition:all .15s}
  .chip:hover{background:var(--sage);color:#fff}
  .input-row{padding:.8rem 1rem;border-top:1px solid rgba(0,0,0,.07);display:flex;gap:.5rem}
  .inp{flex:1;border:1.5px solid rgba(0,0,0,.12);border-radius:10px;padding:.55rem .9rem;font-size:.85rem;font-family:'DM Sans',sans-serif;outline:none;background:var(--bg);transition:border-color .2s}
  .inp:focus{border-color:var(--sage)}
  .send{background:var(--sage);color:#fff;border:none;cursor:pointer;width:38px;height:38px;border-radius:10px;font-size:1rem;display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .send:hover{opacity:.85}

  .overlay{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.4);display:none;justify-content:flex-end}
  .overlay.open{display:flex}
  .drawer{background:#fff;width:340px;height:100vh;overflow-y:auto;padding:1.3rem;animation:slidein .22s ease}
  .drawer h2{font-family:'Fraunces',serif;font-size:1.3rem;margin-bottom:1rem}
  .close{float:right;background:none;border:none;font-size:1.3rem;cursor:pointer;color:#888}
  .ci{display:flex;align-items:center;gap:.7rem;padding:.7rem 0;border-bottom:1px solid rgba(0,0,0,.07)}
  .ci-em{font-size:1.6rem}
  .ci-info{flex:1;font-size:.83rem}
  .ci-name{font-weight:500}
  .ci-price{color:#777;font-size:.77rem}
  .qty-row{display:flex;align-items:center;gap:.35rem;margin-top:.25rem}
  .qb{width:22px;height:22px;border:1px solid rgba(0,0,0,.15);background:none;border-radius:5px;cursor:pointer;font-size:.85rem;transition:all .15s}
  .qb:hover{background:var(--sage);color:#fff;border-color:var(--sage)}
  .totbox{margin-top:1.2rem;background:var(--mist);padding:.9rem;border-radius:10px}
  .trow{display:flex;justify-content:space-between;font-size:.87rem;margin-bottom:.3rem}
  .trow.grand{font-weight:700;font-size:1rem;margin-top:.5rem;padding-top:.5rem;border-top:1px solid rgba(0,0,0,.08)}
  .ckbtn{width:100%;background:#c44b28;color:#fff;border:none;cursor:pointer;padding:.8rem;border-radius:10px;font-size:.95rem;font-weight:600;margin-top:.9rem;font-family:'DM Sans',sans-serif}
  .ckbtn:hover{opacity:.88}
  .empty-msg{text-align:center;padding:2.5rem 1rem;color:#888}

  .toast{position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%) translateY(60px);background:var(--ink);color:#f4f0e8;padding:.6rem 1.2rem;border-radius:30px;font-size:.83rem;font-weight:500;opacity:0;transition:all .28s;z-index:999;white-space:nowrap}
  .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

  @keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  @keyframes slidein{from{transform:translateX(100%)}to{transform:translateX(0)}}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
  @keyframes bounce{0%,80%,100%{transform:scale(.7);opacity:.5}40%{transform:scale(1);opacity:1}}

  @media(max-width:860px){
    .layout{grid-template-columns:1fr}
    .chat{position:fixed;bottom:0;left:0;right:0;top:auto;height:52vh;z-index:50;border-top:2px solid var(--sage)}
    .products{padding-bottom:54vh}
  }
</style>
</head>
<body>

<nav>
  <div class="logo">Shop<span>AI</span></div>
  <button class="cart-btn" onclick="toggleCart()">🛒 Cart <span class="badge" id="badge">0</span></button>
</nav>

<div class="layout">
  <div class="products">
    <div class="section-head">🛍️ Products</div>
    <div class="filters" id="filters"></div>
    <div class="grid" id="grid"></div>
  </div>

  <div class="chat">
    <div class="chat-hd">
      <div class="av">🤖</div>
      <div>
        <h3>ShopBot — AI Assistant</h3>
        <div class="online"><span class="dot"></span> Always ready</div>
      </div>
    </div>
    <div class="msgs" id="msgs"></div>
    <div class="chips">
      <button class="chip" onclick="ask(this)">Best sellers ⭐</button>
      <button class="chip" onclick="ask(this)">Under $50 💚</button>
      <button class="chip" onclick="ask(this)">Electronics 🎧</button>
      <button class="chip" onclick="ask(this)">Gift ideas 🎁</button>
      <button class="chip" onclick="ask(this)">My cart 🛒</button>
      <button class="chip" onclick="ask(this)">Shipping info 📦</button>
    </div>
    <div class="input-row">
      <input class="inp" id="inp" placeholder="Ask me anything..." onkeydown="if(event.key==='Enter')send()">
      <button class="send" onclick="send()">➤</button>
    </div>
  </div>
</div>

<div class="overlay" id="overlay" onclick="if(event.target===this)toggleCart()">
  <div class="drawer">
    <button class="close" onclick="toggleCart()">✕</button>
    <h2>🛒 Your Cart</h2>
    <div id="cart-items"></div>
    <div id="cart-total"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const PRODUCTS = __PRODUCTS__;
let cart = {}, highlighted = new Set();

function buildFilters(){
  const cats = ['All',...new Set(PRODUCTS.map(p=>p.category))];
  document.getElementById('filters').innerHTML = cats.map(c=>
    `<button class="f-btn${c==='All'?' active':''}" onclick="filter('${c}',this)">${c}</button>`
  ).join('');
}

function filter(cat,btn){
  document.querySelectorAll('.f-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active'); render(cat);
}

function render(cat='All'){
  const list = cat==='All'?PRODUCTS:PRODUCTS.filter(p=>p.category===cat);
  document.getElementById('grid').innerHTML = list.map(p=>`
    <div class="card ${highlighted.has(p.id)?'hl':''}" id="p${p.id}">
      <span class="emoji">${p.image}</span>
      <div class="c-name">${p.name}</div>
      <div class="c-meta">
        <span class="c-price">$${p.price.toFixed(2)}</span>
        <span class="c-rating">⭐ ${p.rating}</span>
      </div>
      <div class="c-stock">📦 ${p.stock} left</div>
      <button class="add" onclick="addToCart(${p.id})">Add to Cart</button>
    </div>`).join('');
}

function addToCart(id){
  cart[id]=(cart[id]||0)+1; updateBadge();
  const p=PRODUCTS.find(x=>x.id===id);
  showToast(`${p.image} ${p.name} added!`);
}
function updateBadge(){document.getElementById('badge').textContent=Object.values(cart).reduce((a,b)=>a+b,0);}

function toggleCart(){document.getElementById('overlay').classList.toggle('open');renderCart();}
function renderCart(){
  const ids=Object.keys(cart).map(Number);
  const ci=document.getElementById('cart-items'), ct=document.getElementById('cart-total');
  if(!ids.length){ci.innerHTML='<div class="empty-msg">🛒 Cart is empty!</div>';ct.innerHTML='';return;}
  let sub=0;
  ci.innerHTML=ids.map(id=>{
    const p=PRODUCTS.find(x=>x.id===id),q=cart[id]; sub+=p.price*q;
    return `<div class="ci">
      <span class="ci-em">${p.image}</span>
      <div class="ci-info">
        <div class="ci-name">${p.name}</div>
        <div class="ci-price">$${p.price.toFixed(2)} each</div>
        <div class="qty-row">
          <button class="qb" onclick="chg(${id},-1)">−</button>
          <span>${q}</span>
          <button class="qb" onclick="chg(${id},1)">+</button>
        </div>
      </div>
      <strong>$${(p.price*q).toFixed(2)}</strong>
    </div>`;
  }).join('');
  const ship=sub>=75?0:5.99;
  ct.innerHTML=`<div class="totbox">
    <div class="trow"><span>Subtotal</span><span>$${sub.toFixed(2)}</span></div>
    <div class="trow"><span>Shipping</span><span>${ship===0?'🎉 FREE':'$'+ship.toFixed(2)}</span></div>
    <div class="trow grand"><span>Total</span><span>$${(sub+ship).toFixed(2)}</span></div>
  </div>
  <button class="ckbtn" onclick="showToast('🎉 Order placed! Thank you!')">Checkout →</button>`;
}
function chg(id,d){cart[id]=(cart[id]||0)+d;if(cart[id]<=0)delete cart[id];updateBadge();renderCart();}

function addMsg(text,role){
  const box=document.getElementById('msgs');
  const d=document.createElement('div');
  d.className='msg '+(role==='bot'?'bot':'usr');
  d.innerHTML=role==='bot'?fmt(text):esc(text);
  box.appendChild(d); box.scrollTop=box.scrollHeight;
}
function fmt(t){return t.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\n/g,'<br>');}
function esc(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

function showTyping(){
  const box=document.getElementById('msgs');
  const d=document.createElement('div'); d.className='msg typing'; d.id='typ';
  d.innerHTML='<div class="dots"><span></span><span></span><span></span></div>';
  box.appendChild(d); box.scrollTop=box.scrollHeight;
}
function removeTyping(){const e=document.getElementById('typ');if(e)e.remove();}

async function send(){
  const inp=document.getElementById('inp'); const text=inp.value.trim(); if(!text)return;
  inp.value=''; addMsg(text,'user'); showTyping();
  const cartPayload=Object.entries(cart).map(([id,qty])=>({product_id:+id,qty}));
  try{
    const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:text,cart:cartPayload})});
    const d=await r.json(); removeTyping();
    addMsg(d.response,'bot');
    highlighted=new Set(d.ids||[]);
    render(document.querySelector('.f-btn.active')?.textContent||'All');
    if(d.ids?.length){
      setTimeout(()=>{const el=document.getElementById('p'+d.ids[0]);if(el)el.scrollIntoView({behavior:'smooth',block:'nearest'});},300);
    }
  }catch(e){removeTyping();addMsg('Something went wrong. Try again!','bot');}
}

function ask(btn){document.getElementById('inp').value=btn.textContent.replace(/[^\w\s$]/g,'').trim();send();}

function showToast(msg){
  const t=document.getElementById('toast'); t.textContent=msg; t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),2400);
}

buildFilters(); render();
addMsg("Hey! 👋 I'm **ShopBot**, your shopping assistant!\nTry: *best sellers*, *under $50*, *gift ideas*, or *show electronics*.", 'bot');
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────
# HTTP SERVER
# ─────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = HTML.replace("__PRODUCTS__", json.dumps(PRODUCTS)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path == "/chat":
            length = int(self.headers.get("Content-Length", 0))
            data   = json.loads(self.rfile.read(length))
            msg    = data.get("message", "").strip()
            cart   = data.get("cart", [])
            response, ids = smart_response(msg, cart)
            body = json.dumps({"response": response, "ids": ids}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()


if __name__ == "__main__":
    port = 5000
    print(f"""
╔══════════════════════════════════════╗
║   ShopAI — AI Shopping Assistant    ║
╠══════════════════════════════════════╣
║  Open:  http://localhost:{port}         ║
║  Mode:  Custom AI  (no API needed)  ║
╚══════════════════════════════════════╝
Press Ctrl+C to stop
""")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
