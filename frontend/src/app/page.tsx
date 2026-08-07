'use client';

import React from 'react';
import Link from 'next/link';
import { SearchBar } from '@/components/search/SearchBar';
import { ProductCard } from '@/components/product/ProductCard';
import { Loader } from '@/components/ui/Loader';
import { useProductSearch } from '@/hooks/useProductSearch';
import { Sparkles, Zap, ShieldCheck, ArrowRight, ShoppingCart, Percent, TrendingUp } from 'lucide-react';

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
      <section className="relative overflow-hidden bg-slate-950 text-white pt-24 pb-28 px-4 sm:px-6 lg:px-8 border-b border-slate-800/80">
        {/* Subtle Background Glow Elements */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-sky-500/15 rounded-full blur-[120px] pointer-events-none animate-pulse-glow" />
        <div className="absolute bottom-0 right-10 w-96 h-96 bg-indigo-500/15 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute top-10 left-10 w-80 h-80 bg-purple-500/10 rounded-full blur-[100px] pointer-events-none" />

        <div className="relative max-w-4xl mx-auto text-center space-y-8 z-10">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-sky-500/10 border border-sky-400/30 text-sky-300 text-xs font-semibold backdrop-blur-md shadow-lg shadow-sky-500/10 animate-float">
            <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
            <span>Side-by-Side E-Commerce & Quick-Commerce Price Comparison</span>
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight text-white leading-tight">
            Never Overpay Again. <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-sky-400 via-indigo-300 to-purple-400">
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
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5 text-sky-400" /> Popular Searches:
            </span>
            {QUICK_TAGS.map((tag) => (
              <Link
                key={tag}
                href={`/search?q=${encodeURIComponent(tag)}`}
                className="bg-slate-900/80 hover:bg-slate-800 text-slate-200 hover:text-white px-3.5 py-1.5 rounded-full backdrop-blur-sm transition-all border border-slate-700/60 hover:border-sky-500/50 shadow-sm"
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
          <div className="glass-card glass-card-hover rounded-3xl p-6 flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-sky-500/10 text-sky-400 border border-sky-500/20 flex items-center justify-center shrink-0 shadow-lg shadow-sky-500/10">
              <ShoppingCart className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-white text-base">Multi-Store Search</h3>
              <p className="text-slate-400 text-xs leading-relaxed">
                Scan Amazon, Flipkart, Myntra, Nykaa, and 8+ quick-commerce platforms simultaneously.
              </p>
            </div>
          </div>

          <div className="glass-card glass-card-hover rounded-3xl p-6 flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0 shadow-lg shadow-emerald-500/10">
              <Sparkles className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-white text-base">Best Pick Algorithm</h3>
              <p className="text-slate-400 text-xs leading-relaxed">
                Our smart score balances lowest price, high rating, and review reliability to pick the winner.
              </p>
            </div>
          </div>

          <div className="glass-card glass-card-hover rounded-3xl p-6 flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center shrink-0 shadow-lg shadow-amber-500/10">
              <Zap className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-white text-base">10-Minute Delivery Info</h3>
              <p className="text-slate-400 text-xs leading-relaxed">
                Instantly check delivery ETAs for Blinkit, Zepto, and Instamart next to traditional stores.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Trending Products Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-2 text-sky-400 font-bold text-xs uppercase tracking-wider mb-1">
              <Percent className="w-4 h-4" /> Top Savings Right Now
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Trending Price Comparisons
            </h2>
          </div>

          <Link
            href="/search"
            className="inline-flex items-center gap-1.5 font-bold text-sm text-sky-400 hover:text-sky-300 transition-colors"
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
