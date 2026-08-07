import React from 'react';
import { Platform } from '@/types/product';
import { BestPickBadge } from './BestPickBadge';
import { RatingStars } from './RatingStars';
import { Button } from '@/components/ui/Button';
import { ExternalLink, Clock, CheckCircle2, XCircle, TrendingDown, Award } from 'lucide-react';

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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
              className={`relative rounded-3xl bg-white p-6 transition-all duration-300 flex flex-col justify-between ${
                isBestPick
                  ? 'border-2 border-emerald-500 shadow-xl shadow-emerald-500/10 ring-4 ring-emerald-500/10 scale-[1.02]'
                  : 'border border-slate-200 shadow-sm hover:shadow-md'
              }`}
            >
              {/* Top Banner if Best Pick */}
              {isBestPick && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 z-10">
                  <BestPickBadge score={platform.computedScore} />
                </div>
              )}

              <div>
                {/* Platform Header */}
                <div className="flex items-center justify-between gap-2 mb-4 pt-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 rounded-xl text-sm font-extrabold border ${theme.bg} ${theme.text} ${theme.border}`}
                    >
                      {platform.platformName}
                    </span>
                  </div>

                  {platform.inStock ? (
                    <span className="inline-flex items-center text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                      <CheckCircle2 className="w-3 h-3 mr-1" /> In Stock
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-[11px] font-semibold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-200">
                      <XCircle className="w-3 h-3 mr-1" /> Out of Stock
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
                      <span className="text-sm text-slate-400 line-through font-medium">
                        ₹{platform.originalPrice.toLocaleString('en-IN')}
                      </span>
                    )}
                  </div>

                  {discountPercent > 0 && (
                    <div className="inline-flex items-center gap-1 text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">
                      <TrendingDown className="w-3.5 h-3.5" /> Save {discountPercent}% OFF
                    </div>
                  )}
                </div>

                {/* Details Breakdown */}
                <div className="space-y-3 py-3 border-t border-b border-slate-100 text-xs">
                  {/* Rating */}
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 font-medium">Customer Rating</span>
                    <RatingStars
                      rating={platform.rating}
                      reviewCount={platform.reviewCount}
                      size="sm"
                    />
                  </div>

                  {/* Delivery ETA */}
                  {platform.deliveryEta && (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500 font-medium">Delivery Time</span>
                      <span className="font-semibold text-slate-800 flex items-center gap-1 bg-slate-50 px-2 py-0.5 rounded">
                        <Clock className="w-3.5 h-3.5 text-sky-600" /> {platform.deliveryEta}
                      </span>
                    </div>
                  )}

                  {/* Computed Score Bar */}
                  {platform.computedScore !== undefined && (
                    <div className="space-y-1 pt-1">
                      <div className="flex justify-between text-[11px] font-semibold text-slate-600">
                        <span className="flex items-center gap-1">
                          <Award className="w-3.5 h-3.5 text-amber-500" /> Value Score
                        </span>
                        <span>{platform.computedScore} / 100</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            isBestPick ? 'bg-emerald-500' : 'bg-sky-500'
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
                <a
                  href={platform.deeplink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full"
                >
                  <Button
                    variant={isBestPick ? 'success' : 'primary'}
                    size="lg"
                    className="w-full font-bold shadow-sm"
                    disabled={!platform.inStock}
                  >
                    <span>Buy on {platform.platformName}</span>
                    <ExternalLink className="w-4 h-4 ml-1 opacity-80" />
                  </Button>
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
