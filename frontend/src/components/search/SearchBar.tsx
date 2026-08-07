'use client';

import React, { useState } from 'react';
import { Search, X } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface SearchBarProps {
  initialQuery?: string;
  placeholder?: string;
  size?: 'normal' | 'large';
  className?: string;
  onSearch?: (query: string) => void;
}

export function SearchBar({
  initialQuery = '',
  placeholder = 'Search iPhone 15, Amul Milk, Nike Shoes, Sony Headphones...',
  size = 'normal',
  className = '',
  onSearch,
}: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    if (onSearch) {
      onSearch(query.trim());
    } else {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleClear = () => {
    setQuery('');
  };

  const isLarge = size === 'large';

  return (
    <form onSubmit={handleSubmit} className={`relative w-full ${className}`}>
      <div
        className={`relative flex items-center w-full bg-white border rounded-2xl transition-all duration-300 shadow-sm hover:shadow-md focus-within:ring-2 focus-within:ring-sky-500 focus-within:border-sky-500 ${
          isLarge ? 'border-slate-300 p-1.5 md:p-2' : 'border-slate-200 p-1'
        }`}
      >
        <div className="pl-3 text-slate-400">
          <Search className={isLarge ? 'w-6 h-6 text-sky-600' : 'w-5 h-5'} />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className={`w-full bg-transparent border-none text-slate-900 placeholder:text-slate-400 focus:outline-none ${
            isLarge ? 'py-3 px-3 text-base md:text-lg' : 'py-2 px-3 text-sm'
          }`}
        />
        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 transition-colors mr-1"
          >
            <X className="w-4 h-4" />
          </button>
        )}
        <button
          type="submit"
          className={`font-semibold rounded-xl text-white transition-all bg-sky-600 hover:bg-sky-700 active:scale-95 shadow-sm ${
            isLarge ? 'px-6 py-3 text-sm md:text-base' : 'px-4 py-2 text-xs md:text-sm'
          }`}
        >
          Compare Prices
        </button>
      </div>
    </form>
  );
}
