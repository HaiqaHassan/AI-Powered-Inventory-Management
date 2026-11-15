# Verdant — AI-Powered Inventory Management System

A Flask + Python OOP inventory app with a warm beige, sage, olive and earthy-brown interface.

## Features
- Full product CRUD and search by ID, name, or category
- Product and PerishableProduct inheritance
- Inventory dashboard and low/out-of-stock alerts
- Optional Groq AI analysis, reorder suggestions, assistant, and description generator
- Works for basic inventory tasks without a Groq API key
- Responsive interface

## Run locally (macOS)
1. Open this folder in VS Code.
2. In its terminal run:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
3. Add your Groq API key to `.env` (AI is optional; never upload `.env`).
4. Start the app:
   ```bash
   python app.py
   ```
5. Visit http://127.0.0.1:5000

## Environment variables
- `GROQ_API_KEY`: private Groq API key
- `GROQ_MODEL`: model available to your Groq account; default `llama-3.3-70b-versatile`

## OOP classes
- `Product`: product fields, total value, stock status, dictionary conversion.
- `PerishableProduct`: child class with expiry date; overrides `to_dict()` using `super()`.
- `InventoryManager`: JSON persistence, CRUD, search, stock status and statistics.
- `InventoryAI`: Groq communication and AI features.

## API
GET `/api/products` (optional `?q=`), POST `/api/products`, PUT/DELETE `/api/products/<product_id>`, GET `/api/stats`, POST `/api/ai/analyze`, POST `/api/ai/reorder`, POST `/api/ai/ask`, POST `/api/ai/description`, GET `/api/health`.

## GitHub upload
Create a new repository, then from this project folder run:
```bash
git init
git add .
git status
git commit -m "Build AI-powered inventory management system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ai-powered-inventory-management.git
git push -u origin main
```
Replace `YOUR-USERNAME` with your GitHub username. `.gitignore` excludes `.env`.

## Vercel deployment
1. Push this folder to GitHub.
2. Import the repository in Vercel (**Add New → Project**).
3. Add `GROQ_API_KEY` and `GROQ_MODEL` in Vercel Environment Variables.
4. Deploy; `vercel.json` routes requests to `api/index.py`.

**Storage warning:** JSON is appropriate for local learning. Vercel serverless storage is temporary and not shared durable storage, so data changes can disappear. For a real deployment, replace JSON storage with Supabase or PostgreSQL and configure database credentials in Vercel. Add authentication, authorization, CSRF protection, rate limiting, backups, and monitoring before production use.

Reorder quantities are AI planning estimates: sales velocity and supplier lead times are not provided by the sample data.
