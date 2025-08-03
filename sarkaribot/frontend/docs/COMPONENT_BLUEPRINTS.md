# Premium Component Blueprints & Implementation Patterns

## 🎯 Overview

This document provides detailed blueprints for implementing premium UI components inspired by top Sarkari Result websites, with modern React patterns and Tailwind CSS styling.

## 🏗️ Component Architecture

### Design System Foundation

#### Base Utility Functions

```typescript
// src/utils/cn.ts - Class name utility
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

```typescript
// src/utils/formatters.ts - Data formatting utilities
import { formatDistanceToNow, format } from 'date-fns';

export const formatJobDate = (date: string | Date) => {
  return format(new Date(date), 'dd MMM yyyy');
};

export const formatTimeAgo = (date: string | Date) => {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
};

export const formatNumber = (num: number) => {
  return new Intl.NumberFormat('en-IN').format(num);
};

export const calculateDaysRemaining = (endDate: string | Date) => {
  const today = new Date();
  const deadline = new Date(endDate);
  const diffTime = deadline.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};
```

## 📱 Core Component Blueprints

### 1. Enhanced SearchBar Component

```typescript
// src/components/SearchBar.tsx
import React, { useState, useRef, useEffect } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useDebounce } from '@/hooks/useDebounce';
import { cn } from '@/utils/cn';

interface SearchSuggestion {
  id: string;
  text: string;
  type: 'job' | 'category' | 'location' | 'organization';
  count?: number;
}

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  onSuggestionSelect?: (suggestion: SearchSuggestion) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  autoFocus?: boolean;
}

export default function SearchBar({
  placeholder = "Search for government jobs...",
  onSearch,
  onSuggestionSelect,
  className,
  size = 'md',
  autoFocus = false
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const debouncedQuery = useDebounce(query, 300);

  // Mock suggestions - replace with actual API call
  const mockSuggestions: SearchSuggestion[] = [
    { id: '1', text: 'SSC CHSL', type: 'job', count: 245 },
    { id: '2', text: 'Railway Jobs', type: 'category', count: 89 },
    { id: '3', text: 'Delhi', type: 'location', count: 156 },
    { id: '4', text: 'UPSC', type: 'organization', count: 34 },
  ];

  // Fetch suggestions based on debounced query
  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      setLoading(true);
      // Simulate API call
      setTimeout(() => {
        const filtered = mockSuggestions.filter(suggestion =>
          suggestion.text.toLowerCase().includes(debouncedQuery.toLowerCase())
        );
        setSuggestions(filtered);
        setLoading(false);
        setIsOpen(true);
      }, 200);
    } else {
      setSuggestions([]);
      setIsOpen(false);
    }
  }, [debouncedQuery]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev =>
            prev < suggestions.length - 1 ? prev + 1 : prev
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
          break;
        case 'Enter':
          e.preventDefault();
          if (selectedIndex >= 0) {
            handleSuggestionSelect(suggestions[selectedIndex]);
          } else {
            handleSearch();
          }
          break;
        case 'Escape':
          setIsOpen(false);
          setSelectedIndex(-1);
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, suggestions]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = () => {
    if (query.trim()) {
      onSearch?.(query.trim());
      setIsOpen(false);
      inputRef.current?.blur();
    }
  };

  const handleSuggestionSelect = (suggestion: SearchSuggestion) => {
    setQuery(suggestion.text);
    setIsOpen(false);
    onSuggestionSelect?.(suggestion);
  };

  const clearSearch = () => {
    setQuery('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const sizeClasses = {
    sm: 'h-10 text-sm',
    md: 'h-12 text-base',
    lg: 'h-14 text-lg'
  };

  const getSuggestionIcon = (type: SearchSuggestion['type']) => {
    const iconClass = "h-4 w-4 flex-shrink-0";
    switch (type) {
      case 'job':
        return <div className={cn(iconClass, "bg-blue-100 text-blue-600 rounded p-0.5")}>💼</div>;
      case 'category':
        return <div className={cn(iconClass, "bg-green-100 text-green-600 rounded p-0.5")}>📁</div>;
      case 'location':
        return <div className={cn(iconClass, "bg-red-100 text-red-600 rounded p-0.5")}>📍</div>;
      case 'organization':
        return <div className={cn(iconClass, "bg-purple-100 text-purple-600 rounded p-0.5")}>🏛️</div>;
      default:
        return null;
    }
  };

  return (
    <div ref={containerRef} className={cn("relative w-full", className)}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
        </div>

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => {
            if (suggestions.length > 0) setIsOpen(true);
          }}
          className={cn(
            "block w-full pl-10 pr-12 border border-gray-300 rounded-lg bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500",
            sizeClasses[size]
          )}
          placeholder={placeholder}
          autoFocus={autoFocus}
          autoComplete="off"
        />

        {query && (
          <button
            onClick={clearSearch}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <XMarkIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>

      {/* Suggestions Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {loading ? (
            <div className="px-4 py-3 text-sm text-gray-500 flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
              Searching...
            </div>
          ) : suggestions.length > 0 ? (
            <ul className="py-1">
              {suggestions.map((suggestion, index) => (
                <li key={suggestion.id}>
                  <button
                    onClick={() => handleSuggestionSelect(suggestion)}
                    className={cn(
                      "w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center justify-between",
                      selectedIndex === index && "bg-primary-50 text-primary-600"
                    )}
                  >
                    <div className="flex items-center space-x-3">
                      {getSuggestionIcon(suggestion.type)}
                      <span className="text-sm font-medium">{suggestion.text}</span>
                    </div>
                    {suggestion.count && (
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                        {suggestion.count}
                      </span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          ) : query.length >= 2 ? (
            <div className="px-4 py-3 text-sm text-gray-500">
              No suggestions found for "{query}"
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
```

### 2. Advanced JobList with Infinite Scroll

```typescript
// src/components/JobList.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useInfiniteScroll } from '@/hooks/useIntersectionObserver';
import JobCard from './JobCard';
import JobCardSkeleton from './JobCardSkeleton';
import { cn } from '@/utils/cn';

interface Job {
  id: string;
  title: string;
  organization: string;
  location: string;
  totalPosts: number;
  qualification: string;
  lastDate: string;
  publishedDate: string;
  isNew: boolean;
  isHot: boolean;
  isSaved: boolean;
  category: string;
  applyLink?: string;
  slug: string;
}

interface JobListProps {
  jobs?: Job[];
  loading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  onJobSave?: (jobId: string) => void;
  onJobShare?: (job: Job) => void;
  className?: string;
  layout?: 'grid' | 'list';
  emptyState?: React.ReactNode;
}

const JobCardSkeleton = () => (
  <div className="bg-white rounded-xl border border-gray-200 p-6 animate-pulse">
    <div className="flex justify-between items-start mb-4">
      <div className="space-y-2 flex-1">
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
      </div>
      <div className="h-8 w-8 bg-gray-200 rounded-full"></div>
    </div>

    <div className="space-y-2 mb-4">
      <div className="h-3 bg-gray-200 rounded w-1/3"></div>
      <div className="h-3 bg-gray-200 rounded w-1/4"></div>
    </div>

    <div className="flex justify-between items-center">
      <div className="h-3 bg-gray-200 rounded w-1/4"></div>
      <div className="flex space-x-2">
        <div className="h-8 w-20 bg-gray-200 rounded"></div>
        <div className="h-8 w-24 bg-gray-200 rounded"></div>
      </div>
    </div>
  </div>
);

const EmptyState = () => (
  <div className="text-center py-12">
    <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
      <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    </div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
    <p className="text-gray-500 max-w-sm mx-auto">
      We couldn't find any jobs matching your criteria. Try adjusting your search or filters.
    </p>
  </div>
);

export default function JobList({
  jobs = [],
  loading = false,
  hasMore = false,
  onLoadMore,
  onJobSave,
  onJobShare,
  className,
  layout = 'grid',
  emptyState
}: JobListProps) {
  const { setTriggerRef, isVisible } = useInfiniteScroll();
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());

  // Load more when trigger is visible
  useEffect(() => {
    if (isVisible && hasMore && !loading && onLoadMore) {
      onLoadMore();
    }
  }, [isVisible, hasMore, loading, onLoadMore]);

  const handleJobSave = useCallback((jobId: string) => {
    setSavedJobs(prev => {
      const newSet = new Set(prev);
      if (newSet.has(jobId)) {
        newSet.delete(jobId);
      } else {
        newSet.add(jobId);
      }
      return newSet;
    });
    onJobSave?.(jobId);
  }, [onJobSave]);

  const handleJobShare = useCallback((job: Job) => {
    onJobShare?.(job);
  }, [onJobShare]);

  // Show loading skeletons
  const renderSkeletons = (count: number = 6) => {
    return Array.from({ length: count }, (_, index) => (
      <JobCardSkeleton key={`skeleton-${index}`} />
    ));
  };

  // Grid layout classes
  const gridClasses = {
    grid: 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6',
    list: 'space-y-4'
  };

  if (loading && jobs.length === 0) {
    return (
      <div className={cn(gridClasses[layout], className)}>
        {renderSkeletons()}
      </div>
    );
  }

  if (!loading && jobs.length === 0) {
    return emptyState || <EmptyState />;
  }

  return (
    <div className={className}>
      <div className={gridClasses[layout]}>
        {jobs.map((job, index) => (
          <JobCard
            key={job.id}
            job={{
              ...job,
              isSaved: savedJobs.has(job.id)
            }}
            onSave={handleJobSave}
            onShare={handleJobShare}
          />
        ))}

        {/* Loading more indicator */}
        {loading && jobs.length > 0 && renderSkeletons(3)}
      </div>

      {/* Infinite scroll trigger */}
      {hasMore && !loading && (
        <div
          ref={setTriggerRef}
          className="flex justify-center py-8"
        >
          <div className="text-gray-500 text-sm">Loading more jobs...</div>
        </div>
      )}

      {/* No more jobs indicator */}
      {!hasMore && jobs.length > 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500 text-sm">
            You've reached the end! Found {jobs.length} job{jobs.length !== 1 ? 's' : ''}.
          </p>
        </div>
      )}
    </div>
  );
}
```

### 3. Premium Footer Component

```typescript
// src/components/Footer.tsx
import React from 'react';
import { cn } from '@/utils/cn';

const footerLinks = {
  'Quick Links': [
    { name: 'Latest Jobs', href: '/jobs/latest' },
    { name: 'Admit Cards', href: '/jobs/admit-card' },
    { name: 'Answer Keys', href: '/jobs/answer-key' },
    { name: 'Results', href: '/jobs/result' },
    { name: 'Syllabus', href: '/syllabus' },
  ],
  'Job Categories': [
    { name: 'Banking Jobs', href: '/category/banking' },
    { name: 'Railway Jobs', href: '/category/railway' },
    { name: 'SSC Jobs', href: '/category/ssc' },
    { name: 'UPSC Jobs', href: '/category/upsc' },
    { name: 'State Government', href: '/category/state' },
  ],
  'Resources': [
    { name: 'Exam Calendar', href: '/calendar' },
    { name: 'Study Material', href: '/study-material' },
    { name: 'Previous Papers', href: '/previous-papers' },
    { name: 'Mock Tests', href: '/mock-tests' },
    { name: 'Career Guidance', href: '/guidance' },
  ],
  'Support': [
    { name: 'Help Center', href: '/help' },
    { name: 'Contact Us', href: '/contact' },
    { name: 'Privacy Policy', href: '/privacy' },
    { name: 'Terms of Service', href: '/terms' },
    { name: 'Sitemap', href: '/sitemap' },
  ],
};

const socialLinks = [
  {
    name: 'Facebook',
    href: '#',
    icon: (props: React.SVGProps<SVGSVGElement>) => (
      <svg fill="currentColor" viewBox="0 0 24 24" {...props}>
        <path fillRule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clipRule="evenodd" />
      </svg>
    ),
  },
  {
    name: 'Twitter',
    href: '#',
    icon: (props: React.SVGProps<SVGSVGElement>) => (
      <svg fill="currentColor" viewBox="0 0 24 24" {...props}>
        <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
      </svg>
    ),
  },
  {
    name: 'YouTube',
    href: '#',
    icon: (props: React.SVGProps<SVGSVGElement>) => (
      <svg fill="currentColor" viewBox="0 0 24 24" {...props}>
        <path fillRule="evenodd" d="M19.812 5.418c.861.23 1.538.907 1.768 1.768C21.998 8.746 22 12 22 12s0 3.255-.418 4.814a2.504 2.504 0 0 1-1.768 1.768c-1.56.419-7.814.419-7.814.419s-6.255 0-7.814-.419a2.505 2.505 0 0 1-1.768-1.768C2 15.255 2 12 2 12s0-3.255.417-4.814a2.507 2.507 0 0 1 1.768-1.768C5.744 5 11.998 5 11.998 5s6.255 0 7.814.418ZM15.194 12 10 15V9l5.194 3Z" clipRule="evenodd" />
      </svg>
    ),
  },
  {
    name: 'Telegram',
    href: '#',
    icon: (props: React.SVGProps<SVGSVGElement>) => (
      <svg fill="currentColor" viewBox="0 0 24 24" {...props}>
        <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
      </svg>
    ),
  },
];

interface FooterProps {
  className?: string;
}

export default function Footer({ className }: FooterProps) {
  return (
    <footer className={cn("bg-gray-900 text-white", className)}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Newsletter Subscription */}
        <div className="bg-gradient-to-r from-primary-600 to-sarkari-600 rounded-xl p-8 mb-12">
          <div className="max-w-2xl mx-auto text-center">
            <h3 className="text-2xl font-bold text-white mb-4">
              Never Miss a Government Job
            </h3>
            <p className="text-primary-100 mb-6">
              Get instant notifications for new job postings, admit cards, and results directly in your inbox.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email address"
                className="flex-1 px-4 py-3 rounded-lg border-0 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white"
              />
              <button className="px-6 py-3 bg-white text-primary-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors duration-200">
                Subscribe
              </button>
            </div>
            <p className="text-xs text-primary-200 mt-3">
              We respect your privacy. Unsubscribe at any time.
            </p>
          </div>
        </div>

        {/* Footer Links */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="text-lg font-semibold text-white mb-4">{category}</h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-gray-300 hover:text-white transition-colors duration-200 text-sm"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* App Download Section */}
        <div className="border-t border-gray-800 pt-8 mb-8">
          <div className="text-center">
            <h4 className="text-lg font-semibold text-white mb-4">Download Our Mobile App</h4>
            <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
              Get instant job alerts, save your favorite jobs, and apply on the go with our mobile app.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="#"
                className="inline-flex items-center px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200"
              >
                <svg className="w-6 h-6 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                </svg>
                Download for iOS
              </a>
              <a
                href="#"
                className="inline-flex items-center px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200"
              >
                <svg className="w-6 h-6 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3,20.5V3.5C3,2.91 3.34,2.39 3.84,2.15L13.69,12L3.84,21.85C3.34,21.6 3,21.09 3,20.5M16.81,15.12L6.05,21.34L14.54,12.85L16.81,15.12M20.16,10.81C20.5,11.08 20.75,11.5 20.75,12C20.75,12.5 20.53,12.9 20.18,13.18L17.89,14.5L15.39,12L17.89,9.5L20.16,10.81M6.05,2.66L16.81,8.88L14.54,11.15L6.05,2.66Z"/>
                </svg>
                Download for Android
              </a>
            </div>
          </div>
        </div>

        {/* Social Links and Copyright */}
        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col lg:flex-row justify-between items-center">
            <div className="flex items-center space-x-6 mb-4 lg:mb-0">
              <div className="flex items-center">
                <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary-600 to-sarkari-600 flex items-center justify-center mr-3">
                  <span className="text-white font-bold">SB</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">SarkariBot</h3>
                  <p className="text-xs text-gray-400">Government Job Portal</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <div className="flex space-x-6">
                {socialLinks.map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    className="text-gray-400 hover:text-white transition-colors duration-200"
                    aria-label={item.name}
                  >
                    <item.icon className="h-6 w-6" />
                  </a>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-gray-800 text-center">
            <p className="text-gray-400 text-sm">
              © {new Date().getFullYear()} SarkariBot. All rights reserved.
            </p>
            <p className="text-gray-500 text-xs mt-2">
              Built with ❤️ for job seekers across India
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
```

### 4. Performance Monitoring Hook

```typescript
// src/hooks/useWebVitals.ts
import { useEffect } from 'react';
import { getCLS, getFCP, getFID, getLCP, getTTFB } from 'web-vitals';

interface WebVitalsMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
}

interface UseWebVitalsOptions {
  enabled?: boolean;
  reportAllChanges?: boolean;
  onMetric?: (metric: WebVitalsMetric) => void;
}

export function useWebVitals({
  enabled = true,
  reportAllChanges = false,
  onMetric
}: UseWebVitalsOptions = {}) {
  useEffect(() => {
    if (!enabled) return;

    const handleMetric = (metric: WebVitalsMetric) => {
      // Log to console in development
      if (process.env.NODE_ENV === 'development') {
        console.log(`${metric.name}:`, metric.value, `(${metric.rating})`);
      }

      // Send to analytics
      onMetric?.(metric);

      // Send to external monitoring service
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', metric.name, {
          event_category: 'Web Vitals',
          event_label: metric.id,
          value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
          non_interaction: true,
        });
      }
    };

    // Measure all Web Vitals
    getCLS(handleMetric, reportAllChanges);
    getFCP(handleMetric, reportAllChanges);
    getFID(handleMetric, reportAllChanges);
    getLCP(handleMetric, reportAllChanges);
    getTTFB(handleMetric, reportAllChanges);
  }, [enabled, reportAllChanges, onMetric]);
}

// Analytics helper
export function sendToAnalytics(metric: WebVitalsMetric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    id: metric.id,
    timestamp: Date.now(),
    url: window.location.href,
    userAgent: navigator.userAgent,
  });

  // Use sendBeacon if available, fallback to fetch
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/web-vitals', body);
  } else {
    fetch('/api/analytics/web-vitals', {
      body,
      method: 'POST',
      keepalive: true,
      headers: {
        'Content-Type': 'application/json',
      },
    }).catch(console.error);
  }
}
```

## 🎨 Advanced Styling Patterns

### Responsive Design Utilities

```css
/* src/styles/responsive.css */
@layer utilities {
  /* Mobile-first spacing */
  .space-mobile {
    @apply space-y-4 md:space-y-6 lg:space-y-8;
  }

  /* Touch-friendly targets */
  .touch-target {
    @apply min-h-[44px] min-w-[44px] flex items-center justify-center;
  }

  /* Safe area handling for mobile */
  .safe-area-top {
    padding-top: env(safe-area-inset-top);
  }

  .safe-area-bottom {
    padding-bottom: env(safe-area-inset-bottom);
  }

  /* Container queries (when supported) */
  @container (min-width: 768px) {
    .container-md\:grid-cols-2 {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  /* Print styles */
  @media print {
    .print\:hidden {
      display: none !important;
    }

    .print\:block {
      display: block !important;
    }
  }
}

/* Animation utilities */
@layer utilities {
  .animate-fade-in-up {
    animation: fadeInUp 0.6s ease-out forwards;
  }

  .animate-slide-in-right {
    animation: slideInRight 0.4s ease-out forwards;
  }

  .animate-scale-in-center {
    animation: scaleInCenter 0.3s ease-out forwards;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleInCenter {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

This comprehensive blueprint provides the foundation for building a premium Sarkari Result-style job portal with modern React patterns, exceptional performance, and mobile-first design principles.
