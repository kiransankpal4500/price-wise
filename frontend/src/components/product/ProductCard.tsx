import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Product } from '@/types/product';
import { RatingStars } from './RatingStars';
import { BestPickBadge } from './BestPickBadge';
import { Button } from '@/components/ui/Button';
import { ArrowRight, ShoppingBag } from 'lucide-react';

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
    <div className="group bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between hover:-translate-y-1">
      <div>
        {/* Image & Header Container */}
        <div className="relative aspect-[4/3] bg-slate-50 overflow-hidden">
          <img
            src={product.mainImage}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute top-3 left-3 flex flex-col gap-1">
            <span className="bg-white/90 backdrop-blur-md px-2.5 py-1 rounded-full text-[11px] font-semibold text-slate-700 shadow-sm border border-slate-100">
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
          <h3 className="font-bold text-slate-900 line-clamp-2 text-base leading-snug group-hover:text-sky-600 transition-colors">
            {product.name}
          </h3>

          <div className="flex items-center justify-between text-xs text-slate-500">
            <RatingStars rating={bestRating} showCount={false} size="sm" />
            <span className="font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
              {product.platforms.length} Stores Compared
            </span>
          </div>

          {/* Platforms Pills */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {product.platforms.slice(0, 4).map((p) => (
              <span
                key={p.platformName}
                className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                  p.platformName === product.bestPickPlatform
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300 font-semibold'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                {p.platformName}: ₹{p.price.toLocaleString('en-IN')}
              </span>
            ))}
            {product.platforms.length > 4 && (
              <span className="text-[10px] px-1.5 py-0.5 text-slate-400">
                +{product.platforms.length - 4} more
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Footer / CTA */}
      <div className="p-5 pt-0 border-t border-slate-100 mt-2 flex items-center justify-between gap-3">
        <div>
          <span className="text-[11px] text-slate-400 block font-medium">Starts from</span>
          <span className="text-lg font-black text-slate-900">
            ₹{lowestPrice.toLocaleString('en-IN')}
          </span>
        </div>

        <Link href={`/product/${product.id}`} className="w-auto">
          <Button variant="secondary" size="sm" className="font-semibold text-xs group-hover:bg-sky-600 group-hover:text-white transition-colors">
            Compare Stores <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
