import { Product } from '@/types/product';
import { calculatePlatformScores } from '@/lib/ranking';

// Dev-only offline fallback dataset matching QuickCommerce API schema for local debugging when backend is un-reachable
const rawProducts: Omit<Product, 'bestPickPlatform'>[] = [
  {
    id: 'apple-iphone-15-128gb',
    name: 'Apple iPhone 15 (128 GB) - Black',
    category: 'Electronics',
    description: 'Dynamic Island, 48MP Main Camera with 2x Telephoto, Super Retina XDR Display, and A16 Bionic chip.',
    mainImage: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop&q=80',
    platforms: [
      {
        platformName: 'Amazon',
        price: 71290,
        originalPrice: 79900,
        rating: 4.6,
        reviewCount: 4520,
        imageUrl: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=300&auto=format&fit=crop&q=80',
        deeplink: 'https://www.amazon.in/dp/B0CHX1W1XY',
        product_url: 'https://www.amazon.in/dp/B0CHX1W1XY',
        deliveryEta: 'Tomorrow, by 10 PM',
        inStock: true,
      },
      {
        platformName: 'Flipkart',
        price: 69999,
        originalPrice: 79900,
        rating: 4.7,
        reviewCount: 8930,
        imageUrl: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=300&auto=format&fit=crop&q=80',
        deeplink: 'https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4',
        product_url: 'https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4',
        deliveryEta: '2 Days',
        inStock: true,
      },
      {
        platformName: 'JioMart',
        price: 72490,
        originalPrice: 79900,
        rating: 4.3,
        reviewCount: 410,
        imageUrl: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=300&auto=format&fit=crop&q=80',
        deeplink: 'https://www.jiomart.com/p/electronics/apple-iphone-15-128-gb-black/600000000',
        product_url: 'https://www.jiomart.com/p/electronics/apple-iphone-15-128-gb-black/600000000',
        deliveryEta: '3-4 Days',
        inStock: true,
      },
      {
        platformName: 'Blinkit',
        price: 74900,
        originalPrice: 79900,
        rating: 4.8,
        deliveryEta: '12 mins',
        imageUrl: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=300&auto=format&fit=crop&q=80',
        deeplink: 'https://blinkit.com/prn/apple-iphone-15-128gb/prid/58912',
        product_url: 'https://blinkit.com/prn/apple-iphone-15-128gb/prid/58912',
        inStock: true,
      },
    ],
  },
  {
    id: 'sony-wh-1000xm5-headphones',
    name: 'Sony WH-1000XM5 Wireless Noise Cancelling Headphones',
    category: 'Electronics',
    description: 'Industry-leading noise canceling with 8 microphones, 30 hours battery life, and crystal clear hands-free calling.',
    mainImage: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80',
    platforms: [
      {
        platformName: 'Amazon',
        price: 26990,
        originalPrice: 34990,
        rating: 4.5,
        reviewCount: 3120,
        imageUrl: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&auto=format&fit=crop&q=80',
        deeplink: 'https://www.amazon.in/dp/B0B56769VT',
        product_url: 'https://www.amazon.in/dp/B0B56769VT',
        deliveryEta: 'Same Day Delivery',
        inStock: true,
      },
      {
        platformName: 'Flipkart',
        price: 27990,
        originalPrice: 34990,
        rating: 4.4,
        reviewCount: 1450,
        imageUrl: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&auto=format&fit=crop&q=80',
        deeplink: 'https://www.flipkart.com/sony-wh-1000xm5-wireless-noise-cancellation-headphones/p/itmf5c5a9dbc3e17',
        product_url: 'https://www.flipkart.com/sony-wh-1000xm5-wireless-noise-cancellation-headphones/p/itmf5c5a9dbc3e17',
        deliveryEta: '2 Days',
        inStock: true,
      },
      {
        platformName: 'Flipkart Minutes',
        price: 28490,
        originalPrice: 34990,
        rating: 4.6,
        deliveryEta: '15 mins',
        imageUrl: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&auto=format&fit=crop&q=80',
        deeplink: 'https://www.flipkart.com/sony-wh-1000xm5-wireless-noise-cancellation-headphones/p/itmf5c5a9dbc3e17',
        product_url: 'https://www.flipkart.com/sony-wh-1000xm5-wireless-noise-cancellation-headphones/p/itmf5c5a9dbc3e17',
        inStock: true,
      },
    ],
  },
];

export const DEV_FALLBACK_PRODUCTS: Product[] = rawProducts.map((p) => {
  const { platformsWithScores, bestPickPlatform } = calculatePlatformScores(p.platforms);
  return {
    ...p,
    platforms: platformsWithScores,
    bestPickPlatform,
  };
});
