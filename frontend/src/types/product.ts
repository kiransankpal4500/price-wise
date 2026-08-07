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
