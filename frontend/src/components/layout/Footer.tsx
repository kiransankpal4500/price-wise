import React from 'react';
import Link from 'next/link';

export function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 text-xs border-t border-slate-800 py-12 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3 md:col-span-2">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-sky-600 flex items-center justify-center text-white font-black text-base">
                P
              </div>
              <span className="font-bold text-lg text-white">PriceWise</span>
            </div>
            <p className="max-w-sm text-slate-400 leading-relaxed">
              Compare prices, ratings, and delivery times across Amazon, Flipkart, Myntra, Nykaa,
              Blinkit, Zepto, Swiggy Instamart, BigBasket, and more in real time.
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="font-bold text-white uppercase text-[11px] tracking-wider">
              Supported Platforms
            </h4>
            <ul className="space-y-1">
              <li>Amazon & Flipkart</li>
              <li>Blinkit & Zepto</li>
              <li>Swiggy Instamart</li>
              <li>Myntra & Nykaa</li>
              <li>BigBasket & DMart</li>
            </ul>
          </div>

          <div className="space-y-2">
            <h4 className="font-bold text-white uppercase text-[11px] tracking-wider">Project Phase</h4>
            <p className="text-slate-400 leading-relaxed">
              Frontend V1 (Mock Data). Backend integration with QuickCommerce & E-Commerce APIs is scheduled for the next phase.
            </p>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px]">
          <p>© {new Date().getFullYear()} PriceWise Inc. All rights reserved.</p>
          <p className="text-slate-500">Built with Next.js, Tailwind CSS & TypeScript.</p>
        </div>
      </div>
    </footer>
  );
}
