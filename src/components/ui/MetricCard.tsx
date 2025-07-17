'use client';

import React from 'react';
import { cn, getStatusColor, getStatusIcon, getTrendIcon } from '@/lib/utils';
import { MetricCardProps } from '@/types';

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  icon,
  status = 'active',
  className,
  children,
}) => {
  const statusColorClass = getStatusColor(status);
  const statusIcon = getStatusIcon(status);
  const trendIcon = trend ? getTrendIcon(trend) : null;

  return (
    <div className={cn('liberation-card hover:border-primary-500/50', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {icon && (
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-200 text-primary-500">
              {icon}
            </div>
          )}
          <div>
            <p className="text-sm font-medium text-white/70">{title}</p>
            <p className="text-2xl font-bold text-primary-500">{value}</p>
            {subtitle && (
              <p className="text-xs text-white/50">{subtitle}</p>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end space-y-1">
          <div className={cn('flex items-center space-x-1', statusColorClass)}>
            <span className="text-xs">{statusIcon}</span>
            <span className="text-xs capitalize">{status}</span>
          </div>
          {trend && (
            <div className="flex items-center space-x-1 text-xs text-white/60">
              <span>{trendIcon}</span>
              <span className="capitalize">{trend}</span>
            </div>
          )}
        </div>
      </div>
      {children && (
        <div className="mt-4 pt-4 border-t border-primary-500/20">
          {children}
        </div>
      )}
    </div>
  );
};

export default MetricCard;
