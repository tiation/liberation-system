'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { NeonButtonProps } from '@/types';

const NeonButton: React.FC<NeonButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  children,
  className,
  ...props
}) => {
  const baseClasses = `
    inline-flex items-center justify-center font-bold rounded-lg
    transition-all duration-300 active:scale-95 disabled:opacity-50
    disabled:cursor-not-allowed focus:outline-none focus:ring-2
    focus:ring-offset-2 focus:ring-offset-dark-200
  `;

  const variantClasses = {
    primary: `
      bg-gradient-to-r from-primary-500 to-primary-600 text-dark-200
      hover:from-primary-400 hover:to-primary-500 hover:shadow-neon
      focus:ring-primary-500 border border-primary-500/50
    `,
    secondary: `
      bg-gradient-to-r from-secondary-500 to-secondary-600 text-dark-200
      hover:from-secondary-400 hover:to-secondary-500 hover:shadow-neon-pink
      focus:ring-secondary-500 border border-secondary-500/50
    `,
    accent: `
      bg-gradient-to-r from-accent-500 to-accent-600 text-dark-200
      hover:from-accent-400 hover:to-accent-500 hover:shadow-neon-yellow
      focus:ring-accent-500 border border-accent-500/50
    `,
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const handleClick = () => {
    if (!disabled && !loading && onClick) {
      onClick();
    }
  };

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      onClick={handleClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-dark-200 border-t-transparent" />
      )}
      <span className={loading ? 'opacity-50' : ''}>{children}</span>
    </button>
  );
};

export default NeonButton;
