import React from 'react';
import Link from 'next/link';
import { ShoppingBag, Check } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-white text-slate-600 text-xs border-t border-slate-200/80 py-12 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3 md:col-span-2">
            <div className="flex items-center gap-3">
              <div className="relative w-9 h-9 rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-600 to-coral-500 p-0.5 shadow-md">
                <div className="w-full h-full bg-white rounded-[10px] flex items-center justify-center relative overflow-hidden">
                  <ShoppingBag className="w-4 h-4 text-violet-700 stroke-[2.2]" />
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-gradient-to-tr from-violet-600 to-coral-500 rounded-full flex items-center justify-center text-white">
                    <Check className="w-2 h-2 stroke-[3]" />
                  </div>
                </div>
              </div>
              <span className="font-extrabold text-xl text-slate-900 tracking-tight">Price<span className="text-brand-gradient">Wise</span></span>
            </div>
            <p className="max-w-sm text-slate-500 leading-relaxed font-normal">
              Approachable Intelligence in Shopping. Compare real-time prices, ratings, and delivery estimates across Amazon, Flipkart, Myntra, Nykaa, Blinkit, Zepto, and Swiggy Instamart.
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">
              Supported Vendors
            </h4>
            <ul className="space-y-1.5 text-slate-500 font-medium">
              <li>Amazon & Flipkart</li>
              <li>Blinkit & Zepto</li>
              <li>Swiggy Instamart</li>
              <li>Myntra & Nykaa</li>
              <li>BigBasket & DMart</li>
            </ul>
          </div>

          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider">Project Phase</h4>
            <p className="text-slate-500 leading-relaxed">
              Frontend V1 (Mock Data). Backend integration with QuickCommerce & E-Commerce APIs scheduled for Phase 2.
            </p>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px]">
          <p>© {new Date().getFullYear()} PriceWise Inc. All rights reserved.</p>
          <p className="text-slate-400 font-medium">Built with Next.js, Tailwind CSS & TypeScript.</p>
        </div>
      </div>
    </footer>
  );
}
