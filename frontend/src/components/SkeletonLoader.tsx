import React from 'react';

interface SkeletonLoaderProps {
  type?: 'article' | 'card' | 'text' | 'chart';
  count?: number;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ type = 'article', count = 1 }) => {
  const renderArticleSkeleton = () => (
    <div className="card animate-pulse">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 space-y-3">
          {/* Title */}
          <div className="skeleton h-6 w-3/4"></div>
          {/* Description */}
          <div className="skeleton h-4 w-full"></div>
          <div className="skeleton h-4 w-5/6"></div>
        </div>
      </div>
      {/* Tags */}
      <div className="flex items-center space-x-2 mb-3">
        <div className="skeleton h-6 w-20"></div>
        <div className="skeleton h-6 w-24"></div>
        <div className="skeleton h-6 w-16"></div>
      </div>
      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-dark-tertiary">
        <div className="skeleton h-4 w-32"></div>
        <div className="flex space-x-2">
          <div className="skeleton h-8 w-20"></div>
          <div className="skeleton h-8 w-20"></div>
        </div>
      </div>
    </div>
  );

  const renderCardSkeleton = () => (
    <div className="card animate-pulse">
      <div className="skeleton h-6 w-1/3 mb-4"></div>
      <div className="skeleton h-4 w-full mb-2"></div>
      <div className="skeleton h-4 w-4/5"></div>
    </div>
  );

  const renderTextSkeleton = () => (
    <div className="animate-pulse space-y-2">
      <div className="skeleton h-4 w-full"></div>
      <div className="skeleton h-4 w-5/6"></div>
      <div className="skeleton h-4 w-4/5"></div>
    </div>
  );

  const renderChartSkeleton = () => (
    <div className="card animate-pulse">
      <div className="skeleton h-6 w-1/4 mb-4"></div>
      <div className="skeleton h-64 w-full"></div>
    </div>
  );

  const renderSkeleton = () => {
    switch (type) {
      case 'article':
        return renderArticleSkeleton();
      case 'card':
        return renderCardSkeleton();
      case 'text':
        return renderTextSkeleton();
      case 'chart':
        return renderChartSkeleton();
      default:
        return renderArticleSkeleton();
    }
  };

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="mb-4">
          {renderSkeleton()}
        </div>
      ))}
    </>
  );
};
