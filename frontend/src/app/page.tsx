'use client';

import React from 'react';
import Link from 'next/link';
import { SearchBar } from '@/components/search/SearchBar';
import { ProductCard } from '@/components/product/ProductCard';
import { Loader } from '@/components/ui/Loader';
import { useProductSearch } from '@/hooks/useProductSearch';
import { Sparkles, Zap, ShieldCheck, ArrowRight, ShoppingCart, Percent } from 'lucide-react';

const QUICK_TAGS = [
  'iPhone 15',
  'Amul Milk',
  'Nike Shoes',
  'Sony Headphones',
  'Nescafe Coffee',
  'Maybelline',
  'Levi\'s Jeans',
];

export default function HomePage() {
  const { products, loading } = useProductSearch({});

  return (
    <div className="space-y-16 pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-sky-900 via-slate-900 to-slate-950 text-white pt-20 pb-24 px-4 sm:px-6 lg:px-8">
        {/* Subtle Background Glow Elements */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-sky-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-10 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-4xl mx-auto text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-sky-500/10 border border-sky-400/30 text-sky-300 text-xs font-semibold backdrop-blur-md">
            <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
            <span>Side-by-Side E-Commerce & Quick-Commerce Price Comparison</span>
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight text-white leading-tight">
            Never Overpay Again. <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-sky-400 via-sky-200 to-indigo-300">
              Find the Lowest Price in Seconds.
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
            Compare prices, ratings, and delivery times across Amazon, Flipkart, Blinkit, Zepto, Swiggy Instamart, Myntra, Nykaa, and more — all in one place.
          </p>

          {/* Main Search Bar */}
          <div className="max-w-2xl mx-auto pt-2">
            <SearchBar size="large" />
          </div>

          {/* Popular Tag Chips */}
          <div className="flex items-center justify-center flex-wrap gap-2 pt-2 text-xs">
            <span className="text-slate-400 font-medium">Popular Searches:</span>
            {QUICK_TAGS.map((tag) => (
              <Link
                key={tag}
                href={`/search?q=${encodeURIComponent(tag)}`}
                className="bg-white/10 hover:bg-white/20 text-slate-200 hover:text-white px-3 py-1 rounded-full backdrop-blur-sm transition-all border border-white/10"
              >
                {tag}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Highlights Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex items-start gap-4 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center shrink-0">
              <ShoppingCart className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-slate-900 text-base">Multi-Store Search</h3>
              <p className="text-slate-500 text-xs leading-relaxed">
                Scan Amazon, Flipkart, Myntra, Nykaa, and 8+ quick-commerce platforms simultaneously.
              </p>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex items-start gap-4 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <Sparkles className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-slate-900 text-base">Best Pick Algorithm</h3>
              <p className="text-slate-500 text-xs leading-relaxed">
                Our smart score balances lowest price, high rating, and review reliability to pick the winner.
              </p>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex items-start gap-4 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
              <Zap className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-slate-900 text-base">10-Minute Delivery Info</h3>
              <p className="text-slate-500 text-xs leading-relaxed">
                Instantly check delivery ETAs for Blinkit, Zepto, and Instamart next to traditional stores.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Trending Products Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-slate-200 pb-4">
          <div>
            <div className="flex items-center gap-2 text-sky-600 font-bold text-xs uppercase tracking-wider mb-1">
              <Percent className="w-4 h-4" /> Top Savings Right Now
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              Trending Price Comparisons
            </h2>
          </div>

          <Link
            href="/search"
            className="inline-flex items-center gap-1.5 font-bold text-sm text-sky-600 hover:text-sky-700 transition-colors"
          >
            View All Products <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <Loader text="Loading trending comparisons..." />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.slice(0, 8).map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
