import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from models import Product, PerishableProduct
from inventory import InventoryManager
from ai_helper import InventoryAI

load_dotenv()
app = Flask(__name__)
inventory = InventoryManager(os.getenv("INVENTORY_DATA_FILE", "data/products.json"))
ai = InventoryAI()

def error(message, status=400):
    return jsonify({"success": False, "error": message}), status

def parse_product(data, old=None):
    required = ["product_id", "name", "category", "price", "quantity", "reorder_level"]
    for field in required:
        if old is None and field not in data:
            raise ValueError(f"{field.replace('_', ' ').title()} is required.")
    def val(key, default=None):
        return data.get(key, getattr(old, key, default))
    pid, name, category = (str(val(k, "")).strip() for k in
                           ("product_id", "name", "category"))
    if not pid or not name or not category:
        raise ValueError("Product ID, name, and category cannot be empty.")
    try:
        price, qty, level = float(val("price")), int(val("quantity")), int(val("reorder_level"))
    except (TypeError, ValueError):
        raise ValueError("Price, quantity, and reorder level must be valid numbers.")
    if min(price, qty, level) < 0 or price > 100000000:
        raise ValueError("Numeric values must be non-negative and price within allowed range.")
    common = dict(product_id=pid, name=name, category=category, price=price,
                  quantity=qty, reorder_level=level,
                  description=str(val("description", "") or "").strip()[:1000])
    kind = data.get("product_type")
    if kind is None and isinstance(old, PerishableProduct):
        kind = "perishable"
    if kind == "perishable":
        return PerishableProduct(**common, expiry_date=str(val("expiry_date", "") or ""))
    return Product(**common)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/products")
def products_list():
    q = request.args.get("q", "").strip()
    items = inventory.search_products(q) if q else inventory.get_all_products()
    return jsonify({"success": True, "products": [
        p.to_dict() | {"stock_status": p.stock_status(), "total_value": p.total_value()}
        for p in items]})

@app.get("/api/stats")
def stats():
    return jsonify({"success": True, "stats": inventory.statistics()})

@app.post("/api/products")
def add_product():
    try:
        item = parse_product(request.get_json(silent=True) or {})
        inventory.add_product(item)
        return jsonify({"success": True, "product": item.to_dict()}), 201
    except ValueError as exc:
        return error(str(exc))

@app.put("/api/products/<product_id>")
def edit_product(product_id):
    old = inventory.get_product(product_id)
    if not old:
        return error("Product not found.", 404)
    try:
        item = parse_product(request.get_json(silent=True) or {}, old)
        if item.product_id != product_id:
            return error("Product ID cannot be changed.")
        inventory.update_product(product_id, item)
        return jsonify({"success": True, "product": item.to_dict()})
    except ValueError as exc:
        return error(str(exc))

@app.delete("/api/products/<product_id>")
def remove_product(product_id):
    try:
        inventory.delete_product(product_id)
        return jsonify({"success": True, "message": "Product deleted."})
    except ValueError as exc:
        return error(str(exc), 404)

@app.post("/api/ai/analyze")
def ai_analyze():
    try:
        return jsonify({"success": True, "result": ai.analyze(inventory.inventory_context())})
    except Exception as exc:
        return error(f"AI service unavailable: {exc}", 503)

@app.post("/api/ai/reorder")
def ai_reorder():
    try:
        return jsonify({"success": True, "result": ai.reorder_suggestions(inventory.inventory_context())})
    except Exception as exc:
        return error(f"AI service unavailable: {exc}", 503)

@app.post("/api/ai/ask")
def ai_ask():
    question = str((request.get_json(silent=True) or {}).get("question", "")).strip()
    if not question:
        return error("Please enter a question.")
    if len(question) > 600:
        return error("Question is too long (maximum 600 characters).")
    try:
        return jsonify({"success": True, "result": ai.ask(question, inventory.inventory_context())})
    except Exception as exc:
        return error(f"AI service unavailable: {exc}", 503)

@app.post("/api/ai/description")
def ai_description():
    data = request.get_json(silent=True) or {}
    details = {k: str(data.get(k, "")).strip()[:250]
               for k in ("name", "category", "price", "description")}
    if not details["name"] or not details["category"]:
        return error("Enter a product name and category first.")
    try:
        return jsonify({"success": True, "result": ai.product_description(details)})
    except Exception as exc:
        return error(f"AI service unavailable: {exc}", 503)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "ai_configured": bool(os.getenv("GROQ_API_KEY"))})

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
            port=int(os.getenv("PORT", 5000)))
