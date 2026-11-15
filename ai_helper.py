import os
from groq import Groq

class InventoryAI:
    def __init__(self):
        key = os.getenv("GROQ_API_KEY", "").strip()
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.client = Groq(api_key=key) if key else None

    def ask(self, prompt, inventory):
        if not self.client:
            raise RuntimeError("AI is not configured. Add GROQ_API_KEY to your .env file.")
        response = self.client.chat.completions.create(
            model=self.model, temperature=0.3, max_tokens=900,
            messages=[
                {"role": "system", "content":
                 "You are a careful inventory analyst. Use only supplied records. "
                 "Do not invent sales trends, suppliers, demand, or lead times. "
                 "Label estimates clearly."},
                {"role": "user", "content": f"Inventory: {inventory}\nRequest: {prompt}"}
            ])
        return response.choices[0].message.content.strip()

    def analyze(self, inventory):
        return self.ask("Analyze stock health, low stock, out-of-stock items, value "
                        "observations and practical next steps.", inventory)

    def reorder_suggestions(self, inventory):
        return self.ask("Suggest reorder priorities and possible quantities. Sales "
                        "velocity and supplier lead times are unknown; label quantities "
                        "as planning estimates. Prioritize out-of-stock items.", inventory)

    def product_description(self, details):
        return self.ask(f"Write a concise professional product description using only "
                        f"these details: {details}. Do not invent specifications.", [])
