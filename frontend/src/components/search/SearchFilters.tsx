'use client';

import React from 'react';
import { Filter, ArrowUpDown, Zap } from 'lucide-react';

interface SearchFiltersProps {
  category: string;
  sortBy: string;
  inStockOnly: boolean;
  onCategoryChange: (cat: string) => void;
  onSortChange: (sort: 'relevance' | 'price_low' | 'price_high' | 'rating') => void;
  onStockToggle: (checked: boolean) => void;
}

const CATEGORIES = ['All', 'Electronics', 'Groceries', 'Fashion', 'Beauty'];

export function SearchFilters({
  category,
  sortBy,
  inStockOnly,
  onCategoryChange,
  onSortChange,
  onStockToggle,
}: SearchFiltersProps) {
  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-4 shadow-sm space-y-4 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
          <span className="text-xs font-semibold text-slate-500 flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => onCategoryChange(cat)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                category.toLowerCase() === cat.toLowerCase()
                  ? 'bg-sky-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Sort & Stock Filters */}
        <div className="flex items-center gap-4 flex-wrap">
          {/* Stock toggle */}
          <label className="inline-flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-100 transition-colors">
            <input
              type="checkbox"
              checked={inStockOnly}
              onChange={(e) => onStockToggle(e.target.checked)}
              className="w-4 h-4 text-sky-600 rounded border-slate-300 focus:ring-sky-500"
            />
            <span className="flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-amber-500" /> In Stock Only
            </span>
          </label>

          {/* Sort dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
              <ArrowUpDown className="w-3.5 h-3.5" /> Sort:
            </span>
            <select
              value={sortBy}
              onChange={(e) =>
                onSortChange(
                  e.target.value as 'relevance' | 'price_low' | 'price_high' | 'rating'
                )
              }
              className="bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-xl px-3 py-1.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-500"
            >
              <option value="relevance">Relevance</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
              <option value="rating">Highest Rating</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
