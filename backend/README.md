# Comparo — Price Comparison Backend (FastAPI)

Backend service built with Python 3.11+ and FastAPI for **Comparo (PriceWise)**. It integrates with the QuickCommerce API to fetch multi-platform product listings, normalizes pricing and metrics, and calculates the **Best Pick Platform** based on a weighted scoring algorithm.

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI entry point & CORS configuration
│   ├── config.py                # Environment variable loader (.env)
│   ├── routes/
│   │   └── product_routes.py    # /search and /compare/{product_id} endpoints
│   ├── services/
│   │   └── quickcommerce_service.py   # QuickCommerce API integration & fallback
│   ├── core/
│   │   └── ranking.py           # Best product recommendation algorithm
│   └── models/
│       └── product_models.py    # Pydantic schemas (Product, Platform, SearchResponse)
├── .env                          # API Key & environment settings (local)
├── .env.example                  # Environment template
├── requirements.txt              # Dependencies list
└── README.md                     # Documentation
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.11 or higher installed on your system.

### 2. Install Dependencies
In the `backend/` directory, install required packages:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file inside `backend/` (or copy from `.env.example`):
```env
QUICKCOMMERCE_API_KEY=f009f00b-ce0d-4170-b5fe-adeaee1099d0
QUICKCOMMERCE_BASE_URL=https://api.quickcommerce.io/v1
HOST=0.0.0.0
PORT=8000
```

### 4. Run the API Server
Start the Uvicorn development server:
```bash
uvicorn app.main:app --reload
```
The backend server will run at: **`http://localhost:8000`**  
Interactive API Docs (Swagger): **`http://localhost:8000/docs`**

---

## 🧮 Recommendation Ranking Algorithm (`app/core/ranking.py`)

The app evaluates all platforms offering the same product using a relative 0–1 normalization within that specific product's set of listings.

### Normalization Rules:
1. **Price Score**: Lower price = higher score (inverse relative linear scale).
   $$\text{Price Score} = \frac{\text{Max Price} - \text{Price}}{\text{Max Price} - \text{Min Price}}$$
2. **Rating Score**: Higher rating = higher score relative to min and max ratings.
   $$\text{Rating Score} = \frac{\text{Rating} - \text{Min Rating}}{\text{Max Rating} - \text{Min Rating}}$$
3. **Review Count Score**: Higher count = higher trust score.
   $$\text{Review Score} = \frac{\text{Review Count} - \text{Min Reviews}}{\text{Max Reviews} - \text{Min Reviews}}$$

### Weighted Formula:
$$\text{Final Score} = (0.40 \times \text{Price Score}) + (0.35 \times \text{Rating Score}) + (0.25 \times \text{Review Score})$$

*Note*: If a platform lacks review count data (common for quick-commerce apps like Blinkit/Zepto), the 25% review weight is excluded for that platform and redistributed proportionally between price ($\frac{0.4}{0.75} \approx 53.3\%$) and rating ($\frac{0.35}{0.75} \approx 46.7\%$).

---

## 🌐 API Endpoints

- **`GET /search?query={product_name}`**: Returns products matching the search query with store pricing and calculated `bestPickPlatform`.
- **`GET /compare/{product_id}`**: Returns single product comparison details, individual store scores (0–100), and winning store details.
- **`GET /docs`**: Interactive OpenAPI Swagger documentation.
