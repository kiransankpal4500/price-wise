import React from 'react';
import Link from 'next/link';
import { Product } from '@/types/product';
import { RatingStars } from './RatingStars';
import { BestPickBadge } from './BestPickBadge';
import { Button } from '@/components/ui/Button';
import { ArrowRight, Sparkles } from 'lucide-react';

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  // Find lowest price
  const prices = product.platforms.map((p) => p.price);
  const lowestPrice = Math.min(...prices);

  // Find max rating
  const ratings = product.platforms.map((p) => p.rating);
  const bestRating = Math.max(...ratings);

  // Find best pick platform object
  const bestPick = product.platforms.find(
    (p) => p.platformName === product.bestPickPlatform
  );

  return (
    <div className="group soft-card overflow-hidden flex flex-col justify-between p-4 bg-white border border-slate-200/80 rounded-[24px]">
      <div>
        {/* Image & Header Container */}
        <div className="relative aspect-[4/3] bg-slate-50 rounded-[18px] overflow-hidden mb-4 border border-slate-100">
          <img
            src={product.mainImage}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />

          <div className="absolute top-3 left-3 flex flex-col gap-1">
            <span className="bg-white/95 backdrop-blur-md px-3 py-1 rounded-full text-[11px] font-bold text-slate-700 shadow-sm border border-slate-200/80">
              {product.category}
            </span>
          </div>

          {bestPick && (
            <div className="absolute top-3 right-3">
              <BestPickBadge score={bestPick.computedScore} />
            </div>
          )}
        </div>

        {/* Content */}
        <div className="space-y-3 px-1">
          <h3 className="font-bold text-slate-900 line-clamp-2 text-base leading-snug group-hover:text-violet-700 transition-colors">
            {product.name}
          </h3>

          <div className="flex items-center justify-between text-xs text-slate-500">
            <RatingStars rating={bestRating} showCount={false} size="sm" />
            <span className="font-semibold bg-violet-50 text-violet-700 px-2.5 py-0.5 rounded-full text-[11px] border border-violet-100">
              {product.platforms.length} Stores Compared
            </span>
          </div>

          {/* Platforms Pills */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {product.platforms.slice(0, 4).map((p) => (
              <span
                key={p.platformName}
                className={`text-[11px] px-2.5 py-0.5 rounded-full font-semibold transition-all ${
                  p.platformName === product.bestPickPlatform
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-300 shadow-sm'
                    : 'bg-slate-100 text-slate-600 border border-slate-200/60'
                }`}
              >
                {p.platformName}: ₹{p.price.toLocaleString('en-IN')}
              </span>
            ))}
            {product.platforms.length > 4 && (
              <span className="text-[10px] px-1.5 py-0.5 text-slate-400 font-medium">
                +{product.platforms.length - 4} more
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Footer / CTA */}
      <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between gap-3 px-1">
        <div>
          <span className="text-[10px] text-slate-400 block font-bold uppercase tracking-wider">Starts from</span>
          <span className="text-xl font-black text-slate-900">
            ₹{lowestPrice.toLocaleString('en-IN')}
          </span>
        </div>

        <Link href={`/product/${product.id}`}>
          <button className="flex items-center gap-1.5 px-4 py-2.5 rounded-full font-bold text-xs text-white bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 shadow-md shadow-violet-500/20 group-hover:scale-105 transition-all">
            <span>Compare Prices</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </Link>
      </div>
    </div>
  );
}
