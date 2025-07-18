'use client';

import React from 'react';
import { cn, formatPercentage } from '@/lib/utils';
import { ProgressBarProps } from '@/types';

const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max,
  label,
  variant = 'primary',
  showPercentage = true,
  className,
  children,
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  const percentageText = formatPercentage(value, max);

  const variantClasses = {
    primary: 'bg-gradient-to-r from-primary-500 to-primary-600',
    secondary: 'bg-gradient-to-r from-secondary-500 to-secondary-600',
    accent: 'bg-gradient-to-r from-accent-500 to-accent-600',
  };

  return (
    <div className={cn('space-y-2', className)}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center">
          {label && (
            <span className="text-sm font-medium text-white/70">{label}</span>
          )}
          {showPercentage && (
            <span className="text-sm font-mono text-primary-500">
              {percentageText}
            </span>
          )}
        </div>
      )}
      <div className="progress-bar">
        <div
          className={cn(
            'progress-fill',
            variantClasses[variant],
            'relative overflow-hidden animate-pulse-neon'
          )}
          style={{ width: `${percentage}%` }}
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse" />
        </div>
      </div>
      {children && (
        <div className="text-xs text-white/50">
          {children}
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
