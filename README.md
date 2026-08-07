# PriceWise — Product Price Comparison Platform

**PriceWise** is a product price comparison platform that allows users to search for products and compare prices, ratings, review counts, and delivery ETAs side by side across top Indian e-commerce and quick-commerce platforms (Amazon, Flipkart, Myntra, Nykaa, Blinkit, Zepto, Swiggy Instamart, BigBasket, DMart, JioMart, Flipkart Minutes).

> **Current Phase: Frontend V1**  
> The project is currently in the **frontend-only phase**. All data is served via realistic mock data matching the QuickCommerce API schema. The Python/FastAPI backend will be added in Phase 2.

---

## 🏗️ Project Architecture

```
price wise/
├── frontend/                  # Next.js 14 App Router, Tailwind CSS & TypeScript
│   ├── src/
│   │   ├── app/               # Pages (Home, Search, Product Comparison Detail)
│   │   ├── components/        # Layout, Search, Product & UI Components
│   │   ├── data/              # Mock products matching QuickCommerce API schema
│   │   ├── hooks/             # useProductSearch hook abstraction
│   │   ├── lib/               # Best Pick ranking algorithm (ranking.ts)
│   │   └── types/             # TypeScript interfaces (Product, Platform)
│   └── package.json
│
├── backend/                   # Python FastAPI Backend (Phase 2 Placeholder)
│   ├── app/
│   ├── requirements.txt
│   └── README.md
│
└── README.md
```

---

## 🚀 Getting Started (Frontend)

### Prerequisites
- Node.js 18+ and npm

### Installation & Run

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the local development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧮 Best Pick Ranking Algorithm

PriceWise scores and highlights the optimal store using a weighted formula in `frontend/src/lib/ranking.ts`:

$$\text{Score} = (\text{Normalized Rating} \times 0.4) + (\text{Normalized Reviews} \times 0.2) + (\text{Inverse Price} \times 0.4)$$

- For quick-commerce platforms missing review counts, the review weight is gracefully redistributed evenly between rating and price.

---

## 📱 Features

- **Home Page (`/`)**: Hero section, interactive search bar, quick category tags, and trending comparison cards.
- **Search Results (`/search`)**: Real-time filtering by Category, Price sort, In-Stock toggle, and result counter.
- **Product Detail (`/product/[id]`)**: Side-by-side store cards, discount percentages, delivery ETAs, score progress bars, direct buy deeplinks, and Best Pick badge.
