'use client';

import React, { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface EnterpriseBackgroundProps {
  variant?: 'matrix' | 'grid' | 'neural' | 'minimal';
  intensity?: 'low' | 'medium' | 'high';
  className?: string;
  children?: React.ReactNode;
}

const EnterpriseBackground: React.FC<EnterpriseBackgroundProps> = ({
  variant = 'grid',
  intensity = 'medium',
  className,
  children,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    if (variant === 'neural' && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const resizeCanvas = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      };

      resizeCanvas();
      window.addEventListener('resize', resizeCanvas);

      // Neural network animation
      const nodes: Array<{ x: number; y: number; vx: number; vy: number; connections: number[] }> = [];
      const nodeCount = intensity === 'high' ? 150 : intensity === 'medium' ? 100 : 50;

      // Initialize nodes
      for (let i = 0; i < nodeCount; i++) {
        nodes.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          connections: [],
        });
      }

      const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update and draw nodes
        nodes.forEach((node, i) => {
          node.x += node.vx;
          node.y += node.vy;

          // Bounce off edges
          if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
          if (node.y < 0 || node.y > canvas.height) node.vy *= -1;

          // Draw node
          ctx.beginPath();
          ctx.arc(node.x, node.y, 2, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(0, 255, 255, 0.6)';
          ctx.fill();

          // Draw connections
          node.connections = [];
          nodes.forEach((otherNode, j) => {
            if (i !== j) {
              const dx = node.x - otherNode.x;
              const dy = node.y - otherNode.y;
              const distance = Math.sqrt(dx * dx + dy * dy);

              if (distance < 100) {
                node.connections.push(j);
                ctx.beginPath();
                ctx.moveTo(node.x, node.y);
                ctx.lineTo(otherNode.x, otherNode.y);
                ctx.strokeStyle = `rgba(0, 255, 255, ${0.3 * (1 - distance / 100)})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
              }
            }
          });
        });

        animationRef.current = requestAnimationFrame(animate);
      };

      animate();

      return () => {
        window.removeEventListener('resize', resizeCanvas);
        if (animationRef.current) {
          cancelAnimationFrame(animationRef.current);
        }
      };
    }
  }, [variant, intensity]);

  const getBackgroundClasses = () => {
    const baseClasses = 'fixed inset-0 pointer-events-none z-0';
    
    switch (variant) {
      case 'matrix':
        return cn(baseClasses, 'matrix-rain');
      case 'grid':
        return cn(baseClasses, 'cyber-grid');
      case 'neural':
        return cn(baseClasses);
      case 'minimal':
        return cn(baseClasses, 'bg-gradient-to-br from-dark-200 via-surface-200 to-dark-200');
      default:
        return cn(baseClasses, 'cyber-grid');
    }
  };

  return (
    <div className={cn('relative', className)}>
      <div className={getBackgroundClasses()}>
        {variant === 'neural' && (
          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full"
            style={{ background: 'transparent' }}
          />
        )}
        {variant === 'matrix' && (
          <div className="absolute inset-0">
            {Array.from({ length: 20 }, (_, i) => (
              <div
                key={i}
                className="absolute w-px h-full bg-gradient-to-b from-transparent via-primary-500/30 to-transparent animate-matrix"
                style={{
                  left: `${(i * 5) % 100}%`,
                  animationDelay: `${i * 0.5}s`,
                  animationDuration: `${15 + Math.random() * 10}s`,
                }}
              />
            ))}
          </div>
        )}
      </div>
      
      <div className="relative z-10">
        {children}
      </div>
      
      {/* Ambient lighting effects */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-0 w-96 h-96 bg-primary-500/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-1/4 right-0 w-80 h-80 bg-secondary-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
        <div className="absolute bottom-1/4 left-1/4 w-72 h-72 bg-accent-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '4s' }} />
      </div>
    </div>
  );
};

export default EnterpriseBackground;
