import React from 'react';

const LoadingSpinner = ({ size = 'default', text = 'Loading...' }) => {
  const sizeClasses = {
    sm: 'w-6 h-6',
    default: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className={`animate-spin rounded-full border-3 border-gray-200 border-t-primary-600 ${sizeClasses[size]}`}></div>
      {text && (
        <p className="mt-4 text-gray-600 text-sm">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
