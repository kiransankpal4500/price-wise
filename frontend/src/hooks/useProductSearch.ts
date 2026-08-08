'use client';

import { useState, useEffect, useCallback } from 'react';
import { Product } from '@/types/product';
import { DEV_FALLBACK_PRODUCTS } from '@/dev-only/mockProducts';

// Base backend URL from env or default to local FastAPI server
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SearchFilters {
  query?: string;
  category?: string;
  sortBy?: 'relevance' | 'price_low' | 'price_high' | 'rating';
  inStockOnly?: boolean;
}

// Hook for searching products via FastAPI backend with resilient fallback to local dataset
export function useProductSearch(initialFilters: SearchFilters = {}) {
  const [filters, setFilters] = useState<SearchFilters>(initialFilters);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = useCallback(async (currentFilters: SearchFilters) => {
    setLoading(true);
    setError(null);

    try {
      // Build query string parameters for backend GET /search endpoint
      const params = new URLSearchParams();
      if (currentFilters.query) params.append('query', currentFilters.query);
      if (currentFilters.category && currentFilters.category !== 'All') {
        params.append('category', currentFilters.category);
      }
      if (currentFilters.sortBy) params.append('sortBy', currentFilters.sortBy);
      if (currentFilters.inStockOnly) params.append('inStockOnly', 'true');

      const url = `${API_BASE_URL}/search?${params.toString()}`;
      
      // Attempt live API fetch from backend server
      const res = await fetch(url, { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        if (data && Array.isArray(data.results)) {
          setProducts(data.results);
          setLoading(false);
          return;
        }
      }
      throw new Error(`API returned status ${res.status}`);
    } catch (err) {
      console.warn('Backend API unavailable, falling back to local dataset:', err);

      // Resilient local fallback filtering matching QuickCommerce schema
      let result = [...DEV_FALLBACK_PRODUCTS];

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

      if (currentFilters.category && currentFilters.category !== 'All') {
        result = result.filter(
          (p) => p.category.toLowerCase() === currentFilters.category?.toLowerCase()
        );
      }

      if (currentFilters.inStockOnly) {
        result = result.filter((p) => p.platforms.some((pl) => pl.inStock));
      }

      if (currentFilters.sortBy) {
        result.sort((a, b) => {
          const minPriceA = Math.min(...a.platforms.map((p) => p.price));
          const minPriceB = Math.min(...b.platforms.map((p) => p.price));
          const maxRatingA = Math.max(...a.platforms.map((p) => p.rating));
          const maxRatingB = Math.max(...b.platforms.map((p) => p.rating));

          if (currentFilters.sortBy === 'price_low') return minPriceA - minPriceB;
          if (currentFilters.sortBy === 'price_high') return minPriceB - minPriceA;
          if (currentFilters.sortBy === 'rating') return maxRatingB - maxRatingA;
          return 0;
        });
      }

      setProducts(result);
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

// Hook for loading product comparison detail via backend GET /compare/{id} endpoint
export function useProductDetail(productId: string) {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProduct() {
      setLoading(true);
      setError(null);

      try {
        const url = `${API_BASE_URL}/compare/${productId}`;
        const res = await fetch(url, { cache: 'no-store' });
        if (res.ok) {
          const data: Product = await res.json();
          if (data && data.id) {
            setProduct(data);
            setLoading(false);
            return;
          }
        }
        throw new Error(`API status ${res.status}`);
      } catch (e) {
        console.warn('Backend detail endpoint unavailable, using local product lookup:', e);
        const found = DEV_FALLBACK_PRODUCTS.find((p) => p.id === productId);
        if (found) {
          setProduct(found);
        } else {
          setError('Product not found.');
        }
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

// Hook for fetching real trending products directly from backend GET /trending endpoint
export function useTrendingProducts() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTrending() {
      setLoading(true);
      setError(null);
      try {
        const url = `${API_BASE_URL}/trending`;
        const res = await fetch(url, { cache: 'no-store' });
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data)) {
            setProducts(data);
            setLoading(false);
            return;
          }
        }
        throw new Error(`Status ${res.status}`);
      } catch (err) {
        console.warn('Backend /trending endpoint unavailable, using local fallback:', err);
        setProducts(DEV_FALLBACK_PRODUCTS);
      } finally {
        setLoading(false);
      }
    }
    loadTrending();
  }, []);

  return { products, loading, error };
}


