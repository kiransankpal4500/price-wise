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
        className={`relative flex items-center w-full bg-white border rounded-full transition-all duration-300 shadow-md hover:shadow-xl focus-within:ring-4 focus-within:ring-violet-500/20 focus-within:border-violet-500 ${
          isLarge ? 'border-slate-200/90 p-2 md:p-2.5' : 'border-slate-200 p-1.5'
        }`}
      >
        <div className="pl-4 text-violet-600">
          <Search className={isLarge ? 'w-6 h-6 text-violet-600' : 'w-5 h-5 text-violet-600'} />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className={`w-full bg-transparent border-none text-slate-900 placeholder:text-slate-400 focus:outline-none ${
            isLarge ? 'py-3.5 px-4 text-base md:text-lg font-medium' : 'py-2 px-3 text-sm font-medium'
          }`}
        />
        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 transition-colors mr-2"
          >
            <X className="w-4 h-4" />
          </button>
        )}
        <button
          type="submit"
          className={`font-bold rounded-full text-white transition-all bg-gradient-to-r from-violet-600 via-indigo-600 to-rose-500 hover:opacity-95 active:scale-95 shadow-md shadow-violet-500/25 shrink-0 ${
            isLarge ? 'px-8 py-3.5 text-base md:text-lg' : 'px-5 py-2.5 text-xs md:text-sm'
          }`}
        >
          Compare Prices
        </button>
      </div>
    </form>
  );
}
