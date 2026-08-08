'use client';

import React, { useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { SearchBar } from '@/components/search/SearchBar';
import { SearchFilters } from '@/components/search/SearchFilters';
import { ProductCard } from '@/components/product/ProductCard';
import { Loader } from '@/components/ui/Loader';
import { useProductSearch } from '@/hooks/useProductSearch';
import { SearchX, Clock, Wifi, WifiOff } from 'lucide-react';

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const initialQuery = searchParams.get('q') || '';
  const initialCategory = searchParams.get('category') || 'All';

  const { products, loading, filters, updateFilters, cacheInfo } = useProductSearch({
    query: initialQuery,
    category: initialCategory,
    sortBy: 'relevance',
    inStockOnly: false,
  });

  // Keep filters in sync if URL params change
  useEffect(() => {
    updateFilters({
      query: initialQuery,
      category: initialCategory,
    });
  }, [initialQuery, initialCategory]);

  const handleSearchSubmit = (newQuery: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (newQuery) {
      params.set('q', newQuery);
    } else {
      params.delete('q');
    }
    router.push(`/search?${params.toString()}`);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Search Header Banner */}
      <div className="bg-slate-900 rounded-3xl p-6 sm:p-8 text-white space-y-4 shadow-xl">
        <div className="max-w-2xl">
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight mb-2">
            Compare Prices & Stores
          </h1>
          <p className="text-slate-300 text-xs sm:text-sm">
            Search any item to see real-time price comparisons across Amazon, Flipkart, Blinkit, Zepto, and more.
          </p>
        </div>

        <SearchBar
          initialQuery={initialQuery}
          onSearch={handleSearchSubmit}
          size="normal"
        />
      </div>

      {/* Filter Bar */}
      <SearchFilters
        category={filters.category || 'All'}
        sortBy={filters.sortBy || 'relevance'}
        inStockOnly={!!filters.inStockOnly}
        onCategoryChange={(cat) => updateFilters({ category: cat })}
        onSortChange={(sort) => updateFilters({ sortBy: sort })}
        onStockToggle={(checked) => updateFilters({ inStockOnly: checked })}
      />

      {/* Cache Status Banner */}
      {cacheInfo && !loading && (
        <div className={`flex items-center gap-2 px-4 py-2.5 rounded-2xl text-xs font-semibold ${
          cacheInfo.cache_status === 'fresh' || cacheInfo.cache_status === 'live'
            ? 'bg-emerald-50 border border-emerald-200 text-emerald-700'
            : cacheInfo.cache_status === 'stale' || cacheInfo.cache_status === 'very_stale'
            ? 'bg-amber-50 border border-amber-200 text-amber-700'
            : 'bg-slate-100 border border-slate-200 text-slate-600'
        }`}>
          {cacheInfo.cache_status === 'fresh' || cacheInfo.cache_status === 'live'
            ? <Wifi className="w-3.5 h-3.5" />
            : cacheInfo.data_source === 'local'
            ? <WifiOff className="w-3.5 h-3.5" />
            : <Clock className="w-3.5 h-3.5" />
          }
          <span>{cacheInfo.message || 'Product data loaded.'}</span>
        </div>
      )}

      {/* Results Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span>
            {filters.query
              ? `Results for "${filters.query}"`
              : filters.category && filters.category !== 'All'
              ? `${filters.category} Comparisons`
              : 'All Comparisons'}
          </span>
          <span className="text-xs bg-slate-200 text-slate-700 px-2.5 py-0.5 rounded-full font-semibold">
            {products.length} found
          </span>
        </h2>
      </div>

      {/* Loading or Results Grid */}
      {loading ? (
        <Loader text="Searching across platforms..." />
      ) : products.length === 0 ? (
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center space-y-4 max-w-md mx-auto my-12">
          <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
            <SearchX className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">No matching products found</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            We couldn't find any products matching your query. Try searching for popular items like <strong className="text-slate-700">"iPhone"</strong>, <strong className="text-slate-700">"Milk"</strong>, or <strong className="text-slate-700">"Coffee"</strong>.
          </p>
          <button
            onClick={() => handleSearchSubmit('')}
            className="text-xs font-bold text-sky-600 hover:text-sky-700 underline pt-2"
          >
            Clear Search Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<Loader text="Loading search..." />}>
      <SearchContent />
    </Suspense>
  );
}

