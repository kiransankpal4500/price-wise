'use client';

import React from 'react';
import Link from 'next/link';
import { SearchBar } from '@/components/search/SearchBar';
import { ProductCard } from '@/components/product/ProductCard';
import { Loader } from '@/components/ui/Loader';
import { useProductSearch } from '@/hooks/useProductSearch';
import {
  Sparkles,
  Zap,
  ArrowRight,
  ShoppingCart,
  Percent,
  TrendingUp,
  Laptop,
  Shirt,
  Apple,
  Home as HomeIcon,
  Dumbbell,
  Sparkle,
  CheckCircle2
} from 'lucide-react';

const QUICK_TAGS = [
  'iPhone 15',
  'Amul Milk',
  'Nike Shoes',
  'Sony Headphones',
  'Nescafe Coffee',
  'Maybelline',
  'Levi\'s Jeans',
];

const CATEGORIES = [
  { name: 'Electronics', icon: Laptop, color: 'from-violet-500 to-indigo-500', href: '/search?category=Electronics' },
  { name: 'Fashion', icon: Shirt, color: 'from-indigo-500 to-blue-500', href: '/search?category=Fashion' },
  { name: 'Grocery', icon: Apple, color: 'from-emerald-500 to-teal-500', href: '/search?category=Grocery' },
  { name: 'Home', icon: HomeIcon, color: 'from-amber-500 to-orange-500', href: '/search?category=Home' },
  { name: 'Sports', icon: Dumbbell, color: 'from-rose-500 to-pink-500', href: '/search?category=Sports' },
  { name: 'Beauty', icon: Sparkle, color: 'from-purple-500 to-pink-500', href: '/search?category=Beauty' },
];

export default function HomePage() {
  const { products, loading } = useProductSearch({});

  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section - Curvy Container with Signature Brand Gradient */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <div className="relative overflow-hidden rounded-[32px] bg-gradient-to-br from-violet-900 via-indigo-950 to-slate-950 text-white p-8 sm:p-12 md:p-16 border border-violet-800/40 shadow-2xl shadow-violet-950/20">
          {/* Subtle Background Glow Elements */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-violet-500/20 to-orange-500/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none" />

          <div className="relative max-w-3xl mx-auto text-center space-y-6 z-10">
            {/* Tagline Pill */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-xs md:text-sm font-semibold backdrop-blur-md shadow-sm">
              <Sparkles className="w-4 h-4 text-coral-400 animate-pulse" />
              <span>Approachable Intelligence in Shopping</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight text-white leading-[1.15]">
              Never Overpay Again. <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-violet-300 via-indigo-200 to-rose-300">
                Find the Lowest Price in Seconds.
              </span>
            </h1>

            {/* Subheading */}
            <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed font-normal">
              Compare real-time prices, ratings, and delivery times across Amazon, Flipkart, Blinkit, Zepto, Swiggy Instamart, Myntra, and Nykaa in one place.
            </p>

            {/* Prominent Pill-Shaped Search Bar */}
            <div className="max-w-2xl mx-auto pt-4">
              <SearchBar size="large" />
            </div>

            {/* Popular Searches */}
            <div className="flex items-center justify-center flex-wrap gap-2 pt-2 text-xs">
              <span className="text-slate-400 font-semibold flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5 text-violet-400" /> Popular Searches:
              </span>
              {QUICK_TAGS.map((tag) => (
                <Link
                  key={tag}
                  href={`/search?q=${encodeURIComponent(tag)}`}
                  className="bg-white/10 hover:bg-white/20 text-slate-200 hover:text-white px-3.5 py-1.5 rounded-full backdrop-blur-md transition-all border border-white/10 font-medium"
                >
                  {tag}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Categorical Browsing Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
            Popular Categories
          </h2>
          <Link href="/search" className="text-xs font-bold text-violet-600 hover:text-violet-700 flex items-center gap-1">
            Browse All <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            return (
              <Link
                key={cat.name}
                href={cat.href}
                className="group soft-card p-5 text-center flex flex-col items-center gap-3 bg-white rounded-[24px] border border-slate-200/80 hover:border-violet-300 transition-all hover:shadow-lg"
              >
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-tr ${cat.color} text-white flex items-center justify-center shadow-md group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className="w-7 h-7 stroke-[2]" />
                </div>
                <span className="font-bold text-sm text-slate-800 group-hover:text-violet-700 transition-colors">
                  {cat.name}
                </span>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Features Highlight */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="soft-card p-6 bg-white rounded-[24px] border border-slate-200/80 flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-violet-100 text-violet-700 flex items-center justify-center shrink-0">
              <ShoppingCart className="w-6 h-6 stroke-[2.2]" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-slate-900 text-base">Multi-Store Search</h3>
              <p className="text-slate-500 text-xs leading-relaxed">
                Scan Amazon, Flipkart, Myntra, Nykaa, and 8+ quick-commerce platforms simultaneously.
              </p>
            </div>
          </div>

          <div className="soft-card p-6 bg-white rounded-[24px] border border-slate-200/80 flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
              <CheckCircle2 className="w-6 h-6 stroke-[2.2]" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-slate-900 text-base">Best Pick Algorithm</h3>
              <p className="text-slate-500 text-xs leading-relaxed">
                Our smart score balances lowest price, high rating, and review reliability to pick the winner.
              </p>
            </div>
          </div>

          <div className="soft-card p-6 bg-white rounded-[24px] border border-slate-200/80 flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center shrink-0">
              <Zap className="w-6 h-6 stroke-[2.2]" />
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
            <div className="flex items-center gap-2 text-violet-600 font-bold text-xs uppercase tracking-wider mb-1">
              <Percent className="w-4 h-4 text-rose-500" /> Top Deals & Comparisons
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Trending Products
            </h2>
          </div>

          <Link
            href="/search"
            className="inline-flex items-center gap-1.5 font-bold text-sm text-violet-600 hover:text-violet-700 transition-colors"
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
