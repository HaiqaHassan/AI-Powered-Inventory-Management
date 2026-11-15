from dataclasses import dataclass

@dataclass
class Product:
    product_id: str
    name: str
    category: str
    price: float
    quantity: int
    reorder_level: int
    description: str = ""

    def total_value(self):
        return round(self.price * self.quantity, 2)

    def stock_status(self):
        if self.quantity <= 0:
            return "Out of Stock"
        if self.quantity <= self.reorder_level:
            return "Low Stock"
        return "In Stock"

    def to_dict(self):
        return {"product_id": self.product_id, "name": self.name,
                "category": self.category, "price": self.price,
                "quantity": self.quantity, "reorder_level": self.reorder_level,
                "description": self.description, "product_type": "standard"}

    @classmethod
    def from_dict(cls, data):
        common = {key: data[key] for key in
                  ("product_id", "name", "category", "price", "quantity", "reorder_level")}
        common["description"] = data.get("description", "")
        if data.get("product_type") == "perishable":
            return PerishableProduct(**common, expiry_date=data.get("expiry_date", ""))
        return cls(**common)

@dataclass
class PerishableProduct(Product):
    expiry_date: str = ""

    def to_dict(self):
        result = super().to_dict()
        result["product_type"] = "perishable"
        result["expiry_date"] = self.expiry_date
        return result
