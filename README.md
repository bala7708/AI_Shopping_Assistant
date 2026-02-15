# AI_Shopping_Assistant
AI Shopping Assistant — Custom AI


# 🛍️ ShopAI — AI Shopping Assistant

A lightweight, fully self-contained Python shopping web app with a built-in rule-based AI assistant. No external APIs, no frameworks, no dependencies — just Python and a browser.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)
![Size](https://img.shields.io/badge/Size-Single%20File-orange)

---

## ✨ Features

- **🤖 Built-in AI Chatbot** — keyword & tag-based smart response engine (no API key needed)
- **🛒 Shopping Cart** — add/remove items, quantity controls, live subtotal
- **📦 Free Shipping Logic** — auto-applies free shipping on orders over $75
- **✨ AI Product Highlighting** — chat recommendations visually highlight matching products
- **🔍 Category Filtering** — filter products by Electronics, Sports, Food & Drink, and more
- **💬 Quick Chips** — one-tap prompts for common queries
- **📱 Responsive Design** — works on desktop and mobile
- **🎨 Clean UI** — styled with Google Fonts, smooth animations, toast notifications

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher (standard library only)

### Run the App

```bash
# Clone the repository
git clone https://github.com/your-username/shopai.git
cd shopai

# Start the server
python ai_shopping_app.py

# Open in your browser
# http://localhost:5000
```

That's it — no `pip install`, no setup, no config.

---

## 🗂️ Project Structure

```
shopai/
│
├── ai_shopping_app.py   # Everything — backend, AI engine, and frontend in one file
└── README.md
```

### Inside `ai_shopping_app.py`

| Section | Description |
|---|---|
| `PRODUCTS` | Catalog of 12 products with name, price, category, rating, stock, and tags |
| `smart_response()` | The AI engine — parses user input and returns a response + product IDs to highlight |
| `HTML` | Full frontend (HTML + CSS + JS) served directly from Python |
| `Handler` | HTTP request handler for `GET /` and `POST /chat` |

---

## 🤖 How the AI Works

The AI uses a **keyword + tag matching** approach — no machine learning or external API required.

When a user sends a message, `smart_response()`:

1. Lowercases and tokenises the input into a word set
2. Checks against a priority list of intent rules (greetings, cart, shipping, budget, categories, etc.)
3. Falls back to fuzzy tag matching across the product catalog
4. Returns a formatted text response + a list of product IDs to highlight in the UI

**Example intents handled:**

| User says | Bot does |
|---|---|
| `"hi"` / `"hello"` | Greeting response |
| `"show electronics"` | Lists all Electronics products |
| `"under $50"` / `"budget $40"` | Filters products by price |
| `"gift ideas"` | Returns curated gift picks |
| `"best sellers"` | Returns top-rated products |
| `"my cart"` | Summarises cart contents and total |
| `"shipping info"` | Explains delivery options |
| `"returns"` | Explains the return policy |
| `"yoga mat"` | Tag match → Sports products |

---

## 🛍️ Product Catalog

The app ships with 12 demo products across 6 categories:

| # | Product | Price | Category |
|---|---|---|---|
| 🎧 | Wireless Headphones | $299.99 | Electronics |
| 🪑 | Ergonomic Office Chair | $449.00 | Furniture |
| ☕ | Cold-Brew Coffee Kit | $34.99 | Food & Drink |
| ⌚ | Smart Fitness Tracker | $129.95 | Electronics |
| 🧘 | Premium Cork Yoga Mat | $78.00 | Sports |
| ⌨️ | Mechanical Keyboard | $159.99 | Electronics |
| 🍶 | Steel Water Bottle | $39.95 | Sports |
| 🌵 | Succulent Garden Set | $29.99 | Home & Garden |
| 🔊 | Bluetooth Speaker | $89.99 | Electronics |
| 📔 | Leather Journal | $24.99 | Stationery |
| 🫖 | Pour-Over Coffee Set | $55.00 | Food & Drink |
| 👟 | Ultralight Running Shoes | $119.99 | Sports |

---

## 🔧 Customisation

### Add or edit products

Edit the `PRODUCTS` list in `ai_shopping_app.py`:

```python
{"id": 13, "name": "My New Product", "price": 49.99, "category": "Electronics",
 "rating": 4.7, "stock": 20, "image": "💡",
 "tags": ["light","smart","home","tech"]}
```

Tags drive the AI's fuzzy matching — the more descriptive, the better.

### Add new AI intents

Inside `smart_response()`, add a new rule block:

```python
if words & {"lamp", "light", "lighting"}:
    picks = [p for p in PRODUCTS if "light" in p["tags"]]
    return "Here are our lighting picks 💡:\n" + "\n".join(fmt(p) for p in picks), ids(picks)
```

### Change the port

At the bottom of the file:

```python
port = 8080   # change from 5000
```

---

## 📡 API Reference

The server exposes two endpoints:

### `GET /`
Returns the full HTML page with embedded product data.

### `POST /chat`
Accepts a JSON body and returns an AI response.

**Request:**
```json
{
  "message": "show me electronics",
  "cart": [
    { "product_id": 1, "qty": 2 }
  ]
}
```

**Response:**
```json
{
  "response": "Our Electronics lineup 🔌:\n🎧 **Wireless Headphones** — $299.99 (⭐4.8)\n...",
  "ids": [1, 4, 6, 9]
}
```

`ids` is a list of product IDs the UI will highlight on the product grid.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 — `http.server`, `json`, `re` |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Fonts | Google Fonts (Fraunces + DM Sans) |
| AI Engine | Custom rule-based keyword matcher |
| Server | Python built-in `HTTPServer` |

---

## 📋 Requirements

- Python 3.8+
- Internet connection (only for Google Fonts in the browser — optional)
- No `pip install` needed

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙌 Contributing

Pull requests are welcome! Some ideas for contributions:

- Add a search bar
- Persist cart with `localStorage`
- Add product detail modals
- Expand the AI with more intent patterns
- Connect a real database for the product catalog

---

> Built with Python's standard library only — no frameworks, no dependencies, just code.
