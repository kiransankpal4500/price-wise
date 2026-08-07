import React from 'react';
import { Star, StarHalf } from 'lucide-react';

interface RatingStarsProps {
  rating: number; // out of 5
  reviewCount?: number;
  showCount?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function RatingStars({
  rating,
  reviewCount,
  showCount = true,
  size = 'sm',
}: RatingStarsProps) {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.4;
  const starSizes = {
    sm: 'w-3.5 h-3.5',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  return (
    <div className="flex items-center space-x-1">
      <div className="flex items-center text-amber-400">
        {[...Array(5)].map((_, i) => {
          if (i < fullStars) {
            return (
              <Star
                key={i}
                className={`${starSizes[size]} fill-amber-400 text-amber-400`}
              />
            );
          }
          if (i === fullStars && hasHalfStar) {
            return (
              <StarHalf
                key={i}
                className={`${starSizes[size]} fill-amber-400 text-amber-400`}
              />
            );
          }
          return (
            <Star
              key={i}
              className={`${starSizes[size]} text-slate-200 fill-slate-100`}
            />
          );
        })}
      </div>
      <span className="text-xs font-bold text-slate-800 ml-1">
        {rating.toFixed(1)}
      </span>
      {showCount && (
        <span className="text-xs text-slate-500 font-normal">
          {reviewCount !== undefined
            ? `(${reviewCount > 999 ? (reviewCount / 1000).toFixed(1) + 'k' : reviewCount})`
            : '(Quick Deal)'}
        </span>
      )}
    </div>
  );
}
