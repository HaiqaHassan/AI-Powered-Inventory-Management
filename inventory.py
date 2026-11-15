import json
from pathlib import Path
from models import Product

class InventoryManager:
    def __init__(self, data_file="data/products.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.products = []
        self.load_inventory()

    def load_inventory(self):
        if not self.data_file.exists():
            self.products = []
            self.save_inventory()
            return
        try:
            rows = json.loads(self.data_file.read_text(encoding="utf-8") or "[]")
            self.products = [Product.from_dict(row) for row in rows]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            self.products = []

    def save_inventory(self):
        self.data_file.write_text(
            json.dumps([p.to_dict() for p in self.products], indent=2),
            encoding="utf-8")

    def get_product(self, product_id):
        return next((p for p in self.products if p.product_id == product_id), None)

    def add_product(self, product):
        if self.get_product(product.product_id):
            raise ValueError("A product with this ID already exists.")
        self.products.append(product)
        self.save_inventory()

    def get_all_products(self):
        return sorted(self.products, key=lambda p: p.name.lower())

    def update_product(self, product_id, updated):
        for index, item in enumerate(self.products):
            if item.product_id == product_id:
                self.products[index] = updated
                self.save_inventory()
                return
        raise ValueError("Product not found.")

    def delete_product(self, product_id):
        item = self.get_product(product_id)
        if not item:
            raise ValueError("Product not found.")
        self.products.remove(item)
        self.save_inventory()

    def search_products(self, query):
        q = query.lower().strip()
        return [p for p in self.products if q in p.product_id.lower()
                or q in p.name.lower() or q in p.category.lower()]

    def low_stock_products(self):
        return [p for p in self.products if 0 < p.quantity <= p.reorder_level]

    def out_of_stock_products(self):
        return [p for p in self.products if p.quantity <= 0]

    def statistics(self):
        return {"total_products": len(self.products),
                "total_units": sum(p.quantity for p in self.products),
                "total_value": round(sum(p.total_value() for p in self.products), 2),
                "low_stock": len(self.low_stock_products()),
                "out_of_stock": len(self.out_of_stock_products())}

    def inventory_context(self):
        return [p.to_dict() | {"stock_status": p.stock_status(),
                               "total_value": p.total_value()}
                for p in self.get_all_products()]
