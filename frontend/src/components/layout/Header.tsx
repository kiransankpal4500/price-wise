'use client';

import React from 'react';
import Link from 'next/link';
import { SearchBar } from '@/components/search/SearchBar';
import { Tag, Sparkles, TrendingUp } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/80 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-md shadow-sky-500/20 group-hover:scale-105 transition-transform">
            P
          </div>
          <div className="flex flex-col">
            <span className="font-black text-xl tracking-tight text-slate-900 leading-none">
              Price<span className="text-sky-600">Wise</span>
            </span>
            <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase">
              Smart Comparison
            </span>
          </div>
        </Link>

        {/* Header Search Input */}
        <div className="hidden md:block flex-1 max-w-xl mx-4">
          <SearchBar size="normal" />
        </div>

        {/* Quick Nav Links */}
        <nav className="flex items-center gap-2">
          <Link
            href="/search"
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-700 hover:text-sky-600 hover:bg-slate-50 rounded-xl transition-colors"
          >
            <TrendingUp className="w-4 h-4 text-sky-500" />
            <span>Compare All</span>
          </Link>
          <Link
            href="/search?category=Electronics"
            className="hidden sm:flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-700 hover:text-sky-600 hover:bg-slate-50 rounded-xl transition-colors"
          >
            <Tag className="w-4 h-4 text-indigo-500" />
            <span>Electronics</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
