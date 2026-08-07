import React from 'react';
import { Sparkles } from 'lucide-react';

interface BestPickBadgeProps {
  score?: number;
  className?: string;
}

export function BestPickBadge({ score, className = '' }: BestPickBadgeProps) {
  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-full text-xs font-extrabold shadow-lg shadow-emerald-500/30 border border-emerald-300/40 tracking-wide uppercase glow-bestpick ${className}`}
    >
      <Sparkles className="w-3.5 h-3.5 animate-pulse text-amber-300" />
      <span>Best Pick</span>
      {score !== undefined && (
        <span className="bg-emerald-950/40 px-1.5 py-0.5 rounded-full text-[10px] font-mono tracking-normal text-emerald-100 border border-emerald-400/30">
          {score}/100
        </span>
      )}
    </div>
  );
}
