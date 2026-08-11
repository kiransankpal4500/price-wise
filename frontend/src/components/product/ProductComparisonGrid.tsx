import React from 'react';
import { Platform } from '@/types/product';
import { BestPickBadge } from './BestPickBadge';
import { RatingStars } from './RatingStars';
import { Button } from '@/components/ui/Button';
import { ExternalLink, Clock, CheckCircle2, XCircle, TrendingDown, Award, AlertCircle } from 'lucide-react';

interface ProductComparisonGridProps {
  platforms: Platform[];
  bestPickPlatform?: string;
}

// Brand color badges per platform
const PLATFORM_THEMES: Record<string, { bg: string; text: string; border: string }> = {
  Amazon: { bg: 'bg-amber-50', text: 'text-amber-900', border: 'border-amber-200' },
  Flipkart: { bg: 'bg-blue-50', text: 'text-blue-900', border: 'border-blue-200' },
  'Flipkart Minutes': { bg: 'bg-blue-100', text: 'text-blue-900', border: 'border-blue-300' },
  Blinkit: { bg: 'bg-yellow-100', text: 'text-amber-950', border: 'border-yellow-300' },
  Zepto: { bg: 'bg-purple-100', text: 'text-purple-950', border: 'border-purple-300' },
  'Swiggy Instamart': { bg: 'bg-orange-100', text: 'text-orange-950', border: 'border-orange-300' },
  Myntra: { bg: 'bg-pink-50', text: 'text-pink-900', border: 'border-pink-200' },
  Nykaa: { bg: 'bg-rose-50', text: 'text-rose-900', border: 'border-rose-200' },
  BigBasket: { bg: 'bg-emerald-50', text: 'text-emerald-900', border: 'border-emerald-200' },
  DMart: { bg: 'bg-green-50', text: 'text-green-900', border: 'border-green-200' },
  JioMart: { bg: 'bg-indigo-50', text: 'text-indigo-900', border: 'border-indigo-200' },
};

export function ProductComparisonGrid({
  platforms,
  bestPickPlatform,
}: ProductComparisonGridProps) {
  // Sort platforms: Best pick first, then by price low to high
  const sortedPlatforms = [...platforms].sort((a, b) => {
    if (a.platformName === bestPickPlatform) return -1;
    if (b.platformName === bestPickPlatform) return 1;
    return a.price - b.price;
  });

  return (
    <div className="space-y-6">
      {/* Grid of Platform Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
        {sortedPlatforms.map((platform) => {
          const isBestPick = platform.platformName === bestPickPlatform;
          const discountPercent =
            platform.originalPrice && platform.originalPrice > platform.price
              ? Math.round(
                  ((platform.originalPrice - platform.price) / platform.originalPrice) * 100
                )
              : 0;

          const theme = PLATFORM_THEMES[platform.platformName] || {
            bg: 'bg-slate-50',
            text: 'text-slate-800',
            border: 'border-slate-200',
          };

          return (
            <div
              key={platform.platformName}
              className={`relative rounded-[24px] bg-white p-6 transition-all duration-300 flex flex-col justify-between ${
                isBestPick
                  ? 'border-2 border-emerald-500 shadow-xl shadow-emerald-500/10 ring-4 ring-emerald-500/10 scale-[1.03] z-10 glow-bestpick'
                  : 'border border-slate-200/80 shadow-sm hover:shadow-md hover:-translate-y-1'
              }`}
            >
              {/* Top Banner if Best Pick */}
              {isBestPick && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 z-20">
                  <BestPickBadge score={platform.computedScore} />
                </div>
              )}

              <div>
                {/* Platform Header */}
                <div className="flex items-center justify-between gap-2 mb-4 pt-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3.5 py-1 rounded-full text-xs font-extrabold border ${theme.bg} ${theme.text} ${theme.border}`}
                    >
                      {platform.platformName}
                    </span>
                  </div>

                  {platform.inStock ? (
                    <span className="inline-flex items-center text-[11px] font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" /> In Stock
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-[11px] font-bold text-rose-700 bg-rose-50 px-3 py-1 rounded-full border border-rose-200">
                      <XCircle className="w-3.5 h-3.5 mr-1 text-rose-600" /> Out of Stock
                    </span>
                  )}
                </div>

                {/* Price Display */}
                <div className="space-y-1 mb-4">
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-slate-900">
                      ₹{platform.price.toLocaleString('en-IN')}
                    </span>
                    {platform.originalPrice && platform.originalPrice > platform.price && (
                      <span className="text-sm text-slate-400 line-through font-semibold">
                        ₹{platform.originalPrice.toLocaleString('en-IN')}
                      </span>
                    )}
                  </div>

                  {discountPercent > 0 && (
                    <div className="inline-flex items-center gap-1 text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                      <TrendingDown className="w-3.5 h-3.5" /> Save {discountPercent}% OFF
                    </div>
                  )}
                </div>

                {/* Details Breakdown */}
                <div className="space-y-3 py-3 border-t border-b border-slate-100 text-xs">
                  {/* Rating */}
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 font-semibold">Customer Rating</span>
                    <RatingStars
                      rating={platform.rating}
                      reviewCount={platform.reviewCount}
                      size="sm"
                    />
                  </div>

                  {/* Delivery ETA */}
                  {platform.deliveryEta && (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500 font-semibold">Delivery Estimate</span>
                      <span className="font-bold text-slate-800 flex items-center gap-1 bg-violet-50 text-violet-700 px-2.5 py-0.5 rounded-full border border-violet-100">
                        <Clock className="w-3.5 h-3.5 text-violet-600" /> {platform.deliveryEta}
                      </span>
                    </div>
                  )}

                  {/* Computed Score Bar */}
                  {platform.computedScore !== undefined && (
                    <div className="space-y-1.5 pt-1">
                      <div className="flex justify-between text-[11px] font-bold text-slate-700">
                        <span className="flex items-center gap-1">
                          <Award className="w-3.5 h-3.5 text-amber-500" /> Value Score
                        </span>
                        <span>{platform.computedScore} / 100</span>
                      </div>
                      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden p-0.5">
                        <div
                          className={`h-full rounded-full ${
                            isBestPick ? 'bg-emerald-500' : 'bg-violet-500'
                          }`}
                          style={{ width: `${platform.computedScore}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Buy Button CTA */}
              <div className="pt-5">
                {platform.product_url && platform.product_url !== '#' && platform.product_url !== '' ? (
                  <a
                    href={platform.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full"
                  >
                    <button
                      disabled={!platform.inStock}
                      className={`w-full py-3 px-4 rounded-full font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-md ${
                        !platform.inStock
                          ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'
                          : isBestPick
                          ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-emerald-500/20'
                          : 'bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white shadow-violet-500/20'
                      }`}
                    >
                      <span>{platform.inStock ? `Buy on ${platform.platformName}` : 'Out of Stock'}</span>
                      {platform.inStock && <ExternalLink className="w-4 h-4 opacity-90" />}
                    </button>
                  </a>
                ) : (
                  <button
                    disabled
                    className="w-full py-3 px-4 rounded-full font-bold text-xs flex items-center justify-center gap-2 bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed"
                    title="Exact product URL could not be verified for this store listing"
                  >
                    <AlertCircle className="w-3.5 h-3.5 opacity-70" />
                    <span>Product link unavailable</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
