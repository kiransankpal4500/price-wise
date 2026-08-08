export interface Platform {
  platformName: string;       // "Amazon", "Flipkart", "Myntra", "Blinkit", etc.
  price: number;
  originalPrice?: number;     // for discount display
  rating: number;              // out of 5
  reviewCount?: number;        // optional — quick-commerce platforms may not have this
  imageUrl: string;
  deeplink: string;            // link to product on that platform
  deliveryEta?: string;        // relevant for quick-commerce platforms
  inStock: boolean;
  computedScore?: number;      // calculated score for transparency
}

export interface Product {
  id: string;
  name: string;
  category: string;
  description?: string;
  mainImage: string;
  platforms: Platform[];       // same product's listings across all platforms
  bestPickPlatform?: string;   // computed — which platform wins on score
}

// Cache metadata returned by backend with every product response
export interface CacheInfo {
  last_updated?: string;       // ISO timestamp of when data was last fetched from API
  cache_status: 'fresh' | 'stale' | 'very_stale' | 'live' | 'empty' | 'unavailable' | 'unknown';
  data_source: string;         // 'cache' | 'QuickCommerce' | 'none'
  message?: string;            // human-readable status for the UI
}

// Full search API response shape
export interface SearchApiResponse {
  query?: string;
  total: number;
  results: Product[];
  cache_info?: CacheInfo;
}

// Trending API response shape
export interface TrendingApiResponse {
  total: number;
  results: Product[];
  cache_info?: CacheInfo;
}
