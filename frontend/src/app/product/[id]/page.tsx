'use client';

import React from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useProductDetail } from '@/hooks/useProductSearch';
import { ProductComparisonGrid } from '@/components/product/ProductComparisonGrid';
import { RatingStars } from '@/components/product/RatingStars';
import { BestPickBadge } from '@/components/product/BestPickBadge';
import { Loader } from '@/components/ui/Loader';
import {
  ArrowLeft,
  Sparkles,
  Info,
  Store,
  Tag,
  ShieldCheck,
  TrendingDown,
  Clock,
} from 'lucide-react';

export default function ProductDetailPage() {
  const params = useParams();
  const id = Array.isArray(params.id) ? params.id[0] : params.id;

  const { product, loading, error } = useProductDetail(id || '');

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20">
        <Loader text="Fetching real-time store prices..." size="lg" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center space-y-4">
        <h2 className="text-2xl font-bold text-slate-900">Product Not Found</h2>
        <p className="text-sm text-slate-500">
          The requested product comparison could not be loaded or does not exist.
        </p>
        <Link
          href="/search"
          className="inline-flex items-center gap-2 text-sm font-bold text-sky-600 hover:text-sky-700 underline"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Search Comparisons
        </Link>
      </div>
    );
  }

  const prices = product.platforms.map((p) => p.price);
  const lowestPrice = Math.min(...prices);
  const highestPrice = Math.max(...prices);
  const maxSavings = highestPrice - lowestPrice;

  const bestRating = Math.max(...product.platforms.map((p) => p.rating));
  const bestPickPlatform = product.platforms.find(
    (p) => p.platformName === product.bestPickPlatform
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back link */}
      <div>
        <Link
          href="/search"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-sky-600 transition-colors bg-white px-3 py-1.5 rounded-full border border-slate-200 shadow-sm"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Search Results
        </Link>
      </div>

      {/* Product Summary Hero Card */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-md grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
        {/* Main Product Image */}
        <div className="md:col-span-4 aspect-square rounded-2xl bg-slate-50 overflow-hidden relative border border-slate-100">
          <img
            src={product.mainImage}
            alt={product.name}
            className="w-full h-full object-cover"
          />
          <span className="absolute top-3 left-3 bg-slate-900/90 text-white text-[11px] font-bold px-3 py-1 rounded-full backdrop-blur-md">
            {product.category}
          </span>
        </div>

        {/* Product Details */}
        <div className="md:col-span-8 space-y-5">
          <div className="space-y-2">
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 leading-tight">
              {product.name}
            </h1>
            {product.description && (
              <p className="text-slate-500 text-xs sm:text-sm leading-relaxed max-w-2xl">
                {product.description}
              </p>
            )}
          </div>

          {/* Quick Metrics */}
          <div className="flex flex-wrap items-center gap-6 pt-2 border-t border-slate-100">
            <div>
              <span className="text-[11px] text-slate-400 font-semibold block uppercase">
                Lowest Price
              </span>
              <span className="text-2xl font-black text-emerald-600">
                ₹{lowestPrice.toLocaleString('en-IN')}
              </span>
            </div>

            {maxSavings > 0 && (
              <div>
                <span className="text-[11px] text-slate-400 font-semibold block uppercase">
                  Max Potential Savings
                </span>
                <span className="text-lg font-extrabold text-sky-600 flex items-center gap-1">
                  <TrendingDown className="w-4 h-4" /> ₹{maxSavings.toLocaleString('en-IN')}
                </span>
              </div>
            )}

            <div>
              <span className="text-[11px] text-slate-400 font-semibold block uppercase">
                Best Rating
              </span>
              <RatingStars rating={bestRating} showCount={false} size="md" />
            </div>

            <div>
              <span className="text-[11px] text-slate-400 font-semibold block uppercase">
                Stores Compared
              </span>
              <span className="text-sm font-bold text-slate-800 flex items-center gap-1">
                <Store className="w-4 h-4 text-slate-500" /> {product.platforms.length} Platforms
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Scoring Logic Transparency Explanation */}
      <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-slate-950 text-white rounded-3xl p-6 sm:p-7 shadow-lg border border-emerald-900/50 space-y-3">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-emerald-500/20 rounded-xl text-emerald-400">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h3 className="font-bold text-sm sm:text-base text-white flex items-center gap-2">
                Winning Platform:{' '}
                <span className="text-emerald-400 underline font-black">
                  {product.bestPickPlatform}
                </span>
              </h3>
              <p className="text-slate-300 text-xs">
                Calculated using weighted scores across price, customer ratings, and review reliability.
              </p>
            </div>
          </div>

          {bestPickPlatform && (
            <BestPickBadge score={bestPickPlatform.computedScore} />
          )}
        </div>

        {/* Algorithm Formula Explanation */}
        <div className="bg-white/5 rounded-2xl p-3 border border-white/10 text-[11px] text-slate-300 flex items-center gap-2">
          <Info className="w-4 h-4 text-sky-400 shrink-0" />
          <span>
            <strong>Ranking Formula:</strong> Score = (Rating × 40%) + (Review Count × 20%) + (Lowest Price × 40%). Quick-commerce stores without reviews redistribute review weight to rating & price.
          </span>
        </div>
      </div>

      {/* Comparison Grid Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-black text-slate-900 tracking-tight">
            Side-by-Side Store Listings
          </h2>
          <span className="text-xs text-slate-500 font-medium">
            Sorted by Best Pick & Price
          </span>
        </div>

        <ProductComparisonGrid
          platforms={product.platforms}
          bestPickPlatform={product.bestPickPlatform}
        />
      </div>
    </div>
  );
}
