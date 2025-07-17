'use client';

import React, { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import { ConsoleOutputProps } from '@/types';

const ConsoleOutput: React.FC<ConsoleOutputProps> = ({
  logs,
  maxLines = 100,
  autoScroll = true,
  className,
  children,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  // Limit logs to maxLines
  const displayLogs = logs.slice(-maxLines);

  const formatLogLine = (line: string, index: number): React.ReactNode => {
    const timestamp = new Date().toLocaleTimeString();
    
    // Color coding for different log levels
    let colorClass = 'text-primary-500';
    let prefixIcon = '⚡';
    
    if (line.includes('ERROR') || line.includes('FAILED')) {
      colorClass = 'text-error';
      prefixIcon = '❌';
    } else if (line.includes('WARNING') || line.includes('WARN')) {
      colorClass = 'text-warning';
      prefixIcon = '⚠️';
    } else if (line.includes('SUCCESS') || line.includes('COMPLETED')) {
      colorClass = 'text-success';
      prefixIcon = '✅';
    } else if (line.includes('INFO')) {
      colorClass = 'text-primary-400';
      prefixIcon = 'ℹ️';
    }

    return (
      <div key={index} className={cn('flex items-start space-x-2', colorClass)}>
        <span className="text-xs opacity-60 font-mono w-20 flex-shrink-0">
          {timestamp}
        </span>
        <span className="text-xs">{prefixIcon}</span>
        <span className="text-xs flex-1 font-mono">{line}</span>
      </div>
    );
  };

  return (
    <div className={cn('console-output scrollbar-neon', className)}>
      <div className="flex items-center justify-between mb-2 pb-2 border-b border-primary-500/20">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-error rounded-full animate-pulse" />
          <div className="w-3 h-3 bg-warning rounded-full animate-pulse" />
          <div className="w-3 h-3 bg-success rounded-full animate-pulse" />
          <span className="text-xs text-white/70 ml-2">System Console</span>
        </div>
        <div className="text-xs text-white/50">
          {displayLogs.length} / {maxLines} lines
        </div>
      </div>
      
      <div
        ref={containerRef}
        className="space-y-1 max-h-96 overflow-y-auto"
      >
        {displayLogs.length === 0 ? (
          <div className="text-center py-8 text-white/50">
            <span className="text-2xl">💤</span>
            <p className="text-sm mt-2">No logs yet. System is quiet.</p>
          </div>
        ) : (
          displayLogs.map((log, index) => formatLogLine(log, index))
        )}
      </div>
      
      {children && (
        <div className="mt-4 pt-4 border-t border-primary-500/20">
          {children}
        </div>
      )}
    </div>
  );
};

export default ConsoleOutput;
