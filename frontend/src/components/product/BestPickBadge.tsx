import React from 'react';
import { Sparkles, Info } from 'lucide-react';

interface BestPickBadgeProps {
  score?: number;
  className?: string;
}

export function BestPickBadge({ score, className = '' }: BestPickBadgeProps) {
  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-600 text-white rounded-full text-xs font-bold shadow-md shadow-emerald-500/20 tracking-wide uppercase ${className}`}
    >
      <Sparkles className="w-3.5 h-3.5 animate-pulse text-amber-300" />
      <span>Best Pick</span>
      {score !== undefined && (
        <span className="bg-emerald-800/60 px-1.5 py-0.5 rounded text-[10px] font-mono tracking-normal text-emerald-100">
          {score}/100
        </span>
      )}
    </div>
  );
}
