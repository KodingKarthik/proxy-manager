import React from 'react';

interface SkeletonProps {
  className?: string;
  lines?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '', lines = 1 }) => {
  if (lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={`h-4 bg-panel rounded animate-pulse ${className}`}
            aria-busy="true"
            aria-label="Loading"
          ></div>
        ))}
      </div>
    );
  }

  return (
    <div
      className={`h-4 bg-panel rounded animate-pulse ${className}`}
      aria-busy="true"
      aria-label="Loading"
    ></div>
  );
};

