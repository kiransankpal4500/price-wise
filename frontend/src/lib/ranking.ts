import { Platform } from '@/types/product';

/**
 * Calculates the Best Pick platform based on price, rating, and review count.
 * Formula: score = (normalizedRating * 0.4) + (normalizedReviewCount * 0.2) + (inversePriceScore * 0.4)
 * Gracefully handles missing review counts.
 */
export function calculatePlatformScores(platforms: Platform[]): {
  platformsWithScores: Platform[];
  bestPickPlatform: string;
} {
  if (!platforms || platforms.length === 0) {
    return { platformsWithScores: [], bestPickPlatform: '' };
  }

  // Filter in-stock platforms for computing min/max, but score all platforms
  const prices = platforms.map((p) => p.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);

  const ratings = platforms.map((p) => p.rating);
  const minRating = Math.min(...ratings);
  const maxRating = Math.max(...ratings);

  const reviewCounts = platforms
    .map((p) => p.reviewCount)
    .filter((rc): rc is number => rc !== undefined && rc !== null);

  const minReviews = reviewCounts.length > 0 ? Math.min(...reviewCounts) : 0;
  const maxReviews = reviewCounts.length > 0 ? Math.max(...reviewCounts) : 1;

  let highestScore = -1;
  let bestPlatformName = '';

  const platformsWithScores = platforms.map((platform) => {
    // 1. Price Score (inverse: lower price = higher score)
    let inversePriceScore = 1;
    if (maxPrice > minPrice) {
      inversePriceScore = (maxPrice - platform.price) / (maxPrice - minPrice);
    }

    // 2. Rating Score (higher rating = higher score)
    let normalizedRating = 1;
    if (maxRating > minRating) {
      normalizedRating = (platform.rating - minRating) / (maxRating - minRating);
    } else {
      normalizedRating = platform.rating / 5; // absolute scale if all ratings equal
    }

    // 3. Review Count Score (if available)
    let normalizedReviewCount: number | null = null;
    if (platform.reviewCount !== undefined && platform.reviewCount !== null) {
      if (maxReviews > minReviews) {
        normalizedReviewCount =
          (platform.reviewCount - minReviews) / (maxReviews - minReviews);
      } else {
        normalizedReviewCount = 0.5;
      }
    }

    // Weight allocation
    let ratingWeight = 0.4;
    let priceWeight = 0.4;
    let reviewWeight = 0.2;
    let totalWeight = 1.0;

    let scoreSum = 0;

    if (normalizedReviewCount !== null) {
      scoreSum =
        normalizedRating * ratingWeight +
        normalizedReviewCount * reviewWeight +
        inversePriceScore * priceWeight;
    } else {
      // Gracefully handle missing reviewCount: redistribute weight evenly to rating & price
      ratingWeight = 0.5;
      priceWeight = 0.5;
      totalWeight = 1.0;
      scoreSum = normalizedRating * ratingWeight + inversePriceScore * priceWeight;
    }

    // Deduct slightly if out of stock
    const finalScore = platform.inStock ? scoreSum / totalWeight : (scoreSum / totalWeight) * 0.5;
    const roundedScore = Math.round(finalScore * 100);

    if (finalScore > highestScore) {
      highestScore = finalScore;
      bestPlatformName = platform.platformName;
    }

    return {
      ...platform,
      computedScore: roundedScore,
    };
  });

  return {
    platformsWithScores,
    bestPickPlatform: bestPlatformName,
  };
}
