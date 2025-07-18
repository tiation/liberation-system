'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface HolographicCardProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
  variant?: 'default' | 'enterprise' | 'neural' | 'quantum';
  intensity?: 'low' | 'medium' | 'high';
  interactive?: boolean;
}

const HolographicCard: React.FC<HolographicCardProps> = ({
  title,
  subtitle,
  icon,
  children,
  className,
  variant = 'default',
  intensity = 'medium',
  interactive = true,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (cardRef.current) {
        const rect = cardRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        setMousePosition({ x, y });
      }
    };

    if (interactive && isHovered) {
      document.addEventListener('mousemove', handleMouseMove);
      return () => document.removeEventListener('mousemove', handleMouseMove);
    }
  }, [isHovered, interactive]);

  const getVariantClasses = () => {
    const baseClasses = 'relative overflow-hidden rounded-xl border backdrop-blur-md transition-all duration-500';
    
    switch (variant) {
      case 'enterprise':
        return cn(baseClasses, 'bg-gradient-to-br from-surface-200/50 to-dark-200/50 border-primary-500/30');
      case 'neural':
        return cn(baseClasses, 'bg-gradient-to-br from-secondary-500/10 to-dark-200/50 border-secondary-500/30');
      case 'quantum':
        return cn(baseClasses, 'bg-gradient-to-br from-accent-500/10 to-dark-200/50 border-accent-500/30');
      default:
        return cn(baseClasses, 'bg-gradient-to-br from-surface-200/30 to-dark-200/30 border-primary-500/20');
    }
  };

  const getIntensityStyles = () => {
    const base = {
      transform: isHovered ? 'translateY(-4px) scale(1.02)' : 'translateY(0) scale(1)',
      boxShadow: isHovered 
        ? '0 20px 40px rgba(0, 255, 255, 0.3), inset 0 0 30px rgba(0, 255, 255, 0.1)'
        : '0 8px 16px rgba(0, 255, 255, 0.1), inset 0 0 15px rgba(0, 255, 255, 0.05)',
    };

    switch (intensity) {
      case 'high':
        return {
          ...base,
          boxShadow: isHovered 
            ? '0 30px 60px rgba(0, 255, 255, 0.4), inset 0 0 40px rgba(0, 255, 255, 0.2), 0 0 100px rgba(255, 0, 255, 0.3)'
            : '0 15px 30px rgba(0, 255, 255, 0.2), inset 0 0 20px rgba(0, 255, 255, 0.1)',
        };
      case 'low':
        return {
          ...base,
          boxShadow: isHovered 
            ? '0 10px 20px rgba(0, 255, 255, 0.2), inset 0 0 20px rgba(0, 255, 255, 0.05)'
            : '0 4px 8px rgba(0, 255, 255, 0.1)',
        };
      default:
        return base;
    }
  };

  return (
    <div
      ref={cardRef}
      className={cn(getVariantClasses(), className)}
      style={getIntensityStyles()}
      onMouseEnter={() => interactive && setIsHovered(true)}
      onMouseLeave={() => interactive && setIsHovered(false)}
    >
      {/* Holographic overlay effect */}
      <div
        className="absolute inset-0 opacity-0 transition-opacity duration-500"
        style={{
          opacity: isHovered ? 0.3 : 0,
          background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(0, 255, 255, 0.3), transparent 50%)`,
        }}
      />

      {/* Scanning line effect */}
      <div
        className={cn(
          'absolute inset-0 opacity-0 transition-opacity duration-500',
          isHovered && 'opacity-100'
        )}
      >
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-primary-500 to-transparent animate-pulse" />
        <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-primary-500 to-transparent animate-pulse" />
        <div className="absolute top-0 left-0 w-px h-full bg-gradient-to-b from-transparent via-primary-500 to-transparent animate-pulse" />
        <div className="absolute top-0 right-0 w-px h-full bg-gradient-to-b from-transparent via-primary-500 to-transparent animate-pulse" />
      </div>

      {/* Content */}
      <div className="relative z-10 p-6">
        {/* Header */}
        <div className="flex items-center space-x-4 mb-4">
          {icon && (
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-500/20 text-primary-500 animate-pulse-neon">
              {icon}
            </div>
          )}
          <div>
            <h3 className="text-xl font-bold gradient-text-cyan text-shadow-neon">
              {title}
            </h3>
            {subtitle && (
              <p className="text-sm text-white/70 mt-1">{subtitle}</p>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="space-y-4">
          {children}
        </div>
      </div>

      {/* Corner decorations */}
      <div className="absolute top-2 left-2 w-4 h-4 border-l-2 border-t-2 border-primary-500/50" />
      <div className="absolute top-2 right-2 w-4 h-4 border-r-2 border-t-2 border-primary-500/50" />
      <div className="absolute bottom-2 left-2 w-4 h-4 border-l-2 border-b-2 border-primary-500/50" />
      <div className="absolute bottom-2 right-2 w-4 h-4 border-r-2 border-b-2 border-primary-500/50" />

      {/* Data stream effect */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full opacity-20">
          {Array.from({ length: 5 }, (_, i) => (
            <div
              key={i}
              className="absolute w-px h-8 bg-primary-500 animate-pulse"
              style={{
                left: `${20 + i * 20}%`,
                top: `${10 + i * 15}%`,
                animationDelay: `${i * 0.5}s`,
                animationDuration: `${2 + i * 0.3}s`,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default HolographicCard;
