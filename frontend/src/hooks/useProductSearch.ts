'use client';

import { useState, useEffect, useCallback } from 'react';
import { Product } from '@/types/product';
import { MOCK_PRODUCTS } from '@/data/mockProducts';

interface SearchFilters {
  query?: string;
  category?: string;
  sortBy?: 'relevance' | 'price_low' | 'price_high' | 'rating';
  inStockOnly?: boolean;
}

export function useProductSearch(initialFilters: SearchFilters = {}) {
  const [filters, setFilters] = useState<SearchFilters>(initialFilters);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = useCallback(async (currentFilters: SearchFilters) => {
    setLoading(true);
    setError(null);

    try {
      // Simulate real API latency
      await new Promise((resolve) => setTimeout(resolve, 300));

      let result = [...MOCK_PRODUCTS];

      // Query filter
      if (currentFilters.query && currentFilters.query.trim() !== '') {
        const q = currentFilters.query.toLowerCase().trim();
        result = result.filter(
          (p) =>
            p.name.toLowerCase().includes(q) ||
            p.category.toLowerCase().includes(q) ||
            p.description?.toLowerCase().includes(q) ||
            p.platforms.some((pl) => pl.platformName.toLowerCase().includes(q))
        );
      }

      // Category filter
      if (currentFilters.category && currentFilters.category !== 'All') {
        result = result.filter(
          (p) => p.category.toLowerCase() === currentFilters.category?.toLowerCase()
        );
      }

      // Stock filter
      if (currentFilters.inStockOnly) {
        result = result.filter((p) => p.platforms.some((pl) => pl.inStock));
      }

      // Sorting
      if (currentFilters.sortBy) {
        result.sort((a, b) => {
          const minPriceA = Math.min(...a.platforms.map((p) => p.price));
          const minPriceB = Math.min(...b.platforms.map((p) => p.price));
          const maxRatingA = Math.max(...a.platforms.map((p) => p.rating));
          const maxRatingB = Math.max(...b.platforms.map((p) => p.rating));

          if (currentFilters.sortBy === 'price_low') {
            return minPriceA - minPriceB;
          }
          if (currentFilters.sortBy === 'price_high') {
            return minPriceB - minPriceA;
          }
          if (currentFilters.sortBy === 'rating') {
            return maxRatingB - maxRatingA;
          }
          return 0; // relevance default
        });
      }

      setProducts(result);
    } catch (err) {
      setError('Failed to fetch search results. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts(filters);
  }, [filters, fetchProducts]);

  const updateFilters = (newFilters: Partial<SearchFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  return {
    products,
    loading,
    error,
    filters,
    updateFilters,
  };
}

export function useProductDetail(productId: string) {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProduct() {
      setLoading(true);
      setError(null);
      try {
        await new Promise((resolve) => setTimeout(resolve, 250));
        const found = MOCK_PRODUCTS.find((p) => p.id === productId);
        if (found) {
          setProduct(found);
        } else {
          setError('Product not found.');
        }
      } catch (e) {
        setError('Error loading product details.');
      } finally {
        setLoading(false);
      }
    }
    if (productId) {
      loadProduct();
    }
  }, [productId]);

  return { product, loading, error };
}
