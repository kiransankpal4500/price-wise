import React from 'react';

interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'info' | 'accent';
  children: React.ReactNode;
  className?: string;
}

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  const base = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold';

  const variants = {
    default: 'bg-slate-100 text-slate-800 border border-slate-200',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border border-amber-200',
    info: 'bg-sky-50 text-sky-700 border border-sky-200',
    accent: 'bg-purple-50 text-purple-700 border border-purple-200',
  };

  return <span className={`${base} ${variants[variant]} ${className}`}>{children}</span>;
}
