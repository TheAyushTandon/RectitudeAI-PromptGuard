import React from 'react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  color?: string; // Tailwind color class e.g., 'text-primary'
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, icon, color = 'text-white/90' }) => {
  return (
    <div className="bg-white/[0.03] border border-white/5 backdrop-blur-md rounded-2xl p-6 shadow-glass flex flex-col items-center justify-center text-center transition-all hover:bg-white/[0.06] hover:-translate-y-1 group min-h-[140px]">
      <h3 className="text-[10px] font-bold text-white/30 uppercase tracking-[0.3em] mb-4">{title}</h3>
      <div className="flex items-center justify-center gap-3">
        {icon && (
          <div className={cn('text-2xl transition-all group-hover:scale-110', color)}>
            {icon}
          </div>
        )}
        <p className={cn('text-3xl font-sans font-bold tracking-tight transition-all', color)}>
          {value}
        </p>
      </div>
      <div className="absolute inset-x-0 bottom-0 h-[1px] bg-gradient-to-r from-transparent via-white/5 to-transparent" />
    </div>
  );
};

export default MetricCard;
