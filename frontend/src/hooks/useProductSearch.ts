'use client';

import { useState, useEffect, useCallback } from 'react';
import { Product, CacheInfo, SearchApiResponse, TrendingApiResponse } from '@/types/product';
import { DEV_FALLBACK_PRODUCTS } from '@/dev-only/mockProducts';

// Base backend URL from env — points to local FastAPI server (localhost:8000) by default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SearchFilters {
  query?: string;
  category?: string;
  sortBy?: 'relevance' | 'price_low' | 'price_high' | 'rating';
  inStockOnly?: boolean;
}

// ── useProductSearch ──────────────────────────────────────────────────────────
// Fetches products from backend GET /search with cache-first response.
// Falls back to local dev dataset if backend is unreachable.
export function useProductSearch(initialFilters: SearchFilters = {}) {
  const [filters, setFilters] = useState<SearchFilters>(initialFilters);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null);

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

      // Fetch from backend — response includes products + cache metadata
      const res = await fetch(url, { cache: 'no-store' });
      if (res.ok) {
        const data: SearchApiResponse = await res.json();
        if (data && Array.isArray(data.results)) {
          setProducts(data.results);
          // Store cache info so UI can show "Updated X hours ago" banner
          if (data.cache_info) setCacheInfo(data.cache_info);
          return;
        }
      }
      throw new Error(`API returned status ${res.status}`);
    } catch (err) {
      // Backend unavailable — use local dev fallback silently
      console.warn('[PriceWise] Backend unavailable, using local dev fallback:', err);

      let result = [...DEV_FALLBACK_PRODUCTS];

      if (currentFilters.query?.trim()) {
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
      if (currentFilters.sortBy === 'price_low') {
        result.sort((a, b) => Math.min(...a.platforms.map((p) => p.price)) - Math.min(...b.platforms.map((p) => p.price)));
      } else if (currentFilters.sortBy === 'price_high') {
        result.sort((a, b) => Math.min(...b.platforms.map((p) => p.price)) - Math.min(...a.platforms.map((p) => p.price)));
      } else if (currentFilters.sortBy === 'rating') {
        result.sort((a, b) => Math.max(...b.platforms.map((p) => p.rating)) - Math.max(...a.platforms.map((p) => p.rating)));
      }

      setProducts(result);
      // Mark that we're showing dev fallback data
      setCacheInfo({
        cache_status: 'stale',
        data_source: 'local',
        message: 'Backend offline — showing local demo data.',
      });
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

  return { products, loading, error, filters, updateFilters, cacheInfo };
}


// ── useProductDetail ──────────────────────────────────────────────────────────
// Fetches a single product from backend GET /compare/{id} with cache fallback.
export function useProductDetail(productId: string) {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null);

  useEffect(() => {
    async function loadProduct() {
      setLoading(true);
      setError(null);

      try {
        const url = `${API_BASE_URL}/compare/${productId}`;
        const res = await fetch(url, { cache: 'no-store' });
        if (res.ok) {
          const data: Product = await res.json();
          if (data?.id) {
            setProduct(data);
            return;
          }
        }
        throw new Error(`Status ${res.status}`);
      } catch (e) {
        // Backend unavailable — try local dev fallback
        console.warn('[PriceWise] Backend unavailable for product detail:', e);
        const found = DEV_FALLBACK_PRODUCTS.find((p) => p.id === productId);
        if (found) {
          setProduct(found);
          setCacheInfo({
            cache_status: 'stale',
            data_source: 'local',
            message: 'Backend offline — showing local demo data.',
          });
        } else {
          setError('Product not found.');
        }
      } finally {
        setLoading(false);
      }
    }

    if (productId) loadProduct();
  }, [productId]);

  return { product, loading, error, cacheInfo };
}


// ── useTrendingProducts ───────────────────────────────────────────────────────
// Fetches real trending products from backend GET /trending with cache metadata.
// Falls back to local dev data if backend is unreachable.
export function useTrendingProducts() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null);

  useEffect(() => {
    async function loadTrending() {
      setLoading(true);
      setError(null);

      try {
        const res = await fetch(`${API_BASE_URL}/trending`, { cache: 'no-store' });
        if (res.ok) {
          const data: TrendingApiResponse = await res.json();
          if (data && Array.isArray(data.results)) {
            setProducts(data.results);
            // Store cache info so UI can show last_updated banner
            if (data.cache_info) setCacheInfo(data.cache_info);
            return;
          }
        }
        throw new Error(`Status ${res.status}`);
      } catch (err) {
        // Backend unavailable — fall back silently to local dev dataset
        console.warn('[PriceWise] Backend unavailable for trending, using local dev fallback:', err);
        setProducts(DEV_FALLBACK_PRODUCTS);
        setCacheInfo({
          cache_status: 'stale',
          data_source: 'local',
          message: 'Backend offline — showing local demo data.',
        });
      } finally {
        setLoading(false);
      }
    }
    loadTrending();
  }, []);

  return { products, loading, error, cacheInfo };
}
