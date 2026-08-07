'use client';

import React from 'react';
import Link from 'next/link';
import { SearchBar } from '@/components/search/SearchBar';
import { Tag, TrendingUp, ShoppingBag, Check } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-[#f8f9ff]/90 backdrop-blur-xl border-b border-slate-200/60 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
        {/* Brand Logo: Shopping bag merged with checkmark in signature gradient */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative w-12 h-12 rounded-2xl bg-gradient-to-tr from-violet-600 via-indigo-600 to-coral-500 p-0.5 shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform duration-300">
            <div className="w-full h-full bg-white rounded-[14px] flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-tr from-violet-600/10 via-indigo-600/10 to-orange-500/10" />
              <div className="relative flex items-center justify-center">
                <ShoppingBag className="w-6 h-6 text-violet-700 stroke-[2.2]" />
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-gradient-to-tr from-violet-600 to-coral-500 rounded-full flex items-center justify-center text-white shadow-sm">
                  <Check className="w-3 h-3 stroke-[3]" />
                </div>
              </div>
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-2xl tracking-tight text-slate-900 leading-none">
              Price<span className="text-brand-gradient">Wise</span>
            </span>
            <span className="text-[11px] font-semibold text-slate-500 tracking-wide mt-1">
              Approachable Intelligence in Shopping
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
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-bold text-slate-700 hover:text-violet-700 bg-white hover:bg-violet-50/60 rounded-full border border-slate-200/80 shadow-sm transition-all"
          >
            <TrendingUp className="w-4 h-4 text-violet-600" />
            <span>Compare All</span>
          </Link>
          <Link
            href="/search?category=Electronics"
            className="hidden sm:flex items-center gap-2 px-4 py-2.5 text-xs font-bold text-slate-700 hover:text-violet-700 bg-white hover:bg-violet-50/60 rounded-full border border-slate-200/80 shadow-sm transition-all"
          >
            <Tag className="w-4 h-4 text-coral-500" />
            <span>Electronics</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
