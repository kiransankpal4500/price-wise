import React from 'react';
import Link from 'next/link';
import { Product } from '@/types/product';
import { RatingStars } from './RatingStars';
import { BestPickBadge } from './BestPickBadge';
import { Button } from '@/components/ui/Button';
import { ArrowRight } from 'lucide-react';

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
    <div className="group glass-card glass-card-hover rounded-3xl overflow-hidden flex flex-col justify-between">
      <div>
        {/* Image & Header Container */}
        <div className="relative aspect-[4/3] bg-slate-900 overflow-hidden">
          <img
            src={product.mainImage}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-90 group-hover:opacity-100"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-60" />

          <div className="absolute top-3 left-3 flex flex-col gap-1">
            <span className="bg-slate-900/90 backdrop-blur-md px-2.5 py-1 rounded-full text-[11px] font-semibold text-slate-300 shadow-md border border-slate-700/60">
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
        <div className="p-5 space-y-3">
          <h3 className="font-bold text-white line-clamp-2 text-base leading-snug group-hover:text-sky-400 transition-colors">
            {product.name}
          </h3>

          <div className="flex items-center justify-between text-xs text-slate-400">
            <RatingStars rating={bestRating} showCount={false} size="sm" />
            <span className="font-medium bg-slate-800/80 text-slate-300 border border-slate-700/60 px-2 py-0.5 rounded-full text-[10px]">
              {product.platforms.length} Stores
            </span>
          </div>

          {/* Platforms Pills */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {product.platforms.slice(0, 4).map((p) => (
              <span
                key={p.platformName}
                className={`text-[10px] px-2.5 py-0.5 rounded-full font-medium transition-all ${
                  p.platformName === product.bestPickPlatform
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold'
                    : 'bg-slate-800/60 text-slate-400 border border-slate-700/40'
                }`}
              >
                {p.platformName}: ₹{p.price.toLocaleString('en-IN')}
              </span>
            ))}
            {product.platforms.length > 4 && (
              <span className="text-[10px] px-1.5 py-0.5 text-slate-500">
                +{product.platforms.length - 4} more
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Footer / CTA */}
      <div className="p-5 pt-3 border-t border-slate-800/60 flex items-center justify-between gap-3">
        <div>
          <span className="text-[10px] text-slate-400 block font-medium uppercase tracking-wider">Starts from</span>
          <span className="text-xl font-black text-white">
            ₹{lowestPrice.toLocaleString('en-IN')}
          </span>
        </div>

        <Link href={`/product/${product.id}`}>
          <Button variant="primary" size="sm" className="font-semibold text-xs bg-sky-500 hover:bg-sky-400 text-slate-950 border-0 shadow-lg shadow-sky-500/20 group-hover:scale-105 transition-all">
            Compare Stores <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
