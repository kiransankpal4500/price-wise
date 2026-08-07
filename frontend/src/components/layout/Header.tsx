'use client';

import React from 'react';
import Link from 'next/link';
import { SearchBar } from '@/components/search/SearchBar';
import { Tag, Sparkles, TrendingUp } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/60 shadow-2xl shadow-sky-950/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-sky-500 via-indigo-500 to-purple-600 flex items-center justify-center text-white font-black text-xl shadow-lg shadow-sky-500/30 group-hover:scale-105 group-hover:shadow-sky-400/50 transition-all duration-300">
            P
          </div>
          <div className="flex flex-col">
            <span className="font-black text-xl tracking-tight text-white leading-none">
              Price<span className="bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">Wise</span>
            </span>
            <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase flex items-center gap-1">
              Smart Comparison <Sparkles className="w-2.5 h-2.5 text-amber-400 inline" />
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
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 rounded-xl transition-all border border-transparent hover:border-slate-700"
          >
            <TrendingUp className="w-4 h-4 text-sky-400" />
            <span>Compare All</span>
          </Link>
          <Link
            href="/search?category=Electronics"
            className="hidden sm:flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 rounded-xl transition-all border border-transparent hover:border-slate-700"
          >
            <Tag className="w-4 h-4 text-indigo-400" />
            <span>Electronics</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
