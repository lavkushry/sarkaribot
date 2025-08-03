# Premium Sarkari Result Implementation Guide

## 🎯 Implementation Strategy

This document provides a comprehensive implementation roadmap for building a premium government job portal using React 18+ and Tailwind CSS, based on extensive research of top Sarkari Result websites.

## 🏗️ Architecture Overview

### Technology Stack

**Frontend Framework:**

- React 18.2+ with TypeScript
- Tailwind CSS 3.4+ for styling
- Heroicons for consistent iconography
- Headless UI for accessible components
- Framer Motion for smooth animations

**State Management:**

- Zustand for lightweight global state
- React Query (TanStack Query) for server state
- React Hook Form for form management

**Performance & PWA:**

- Vite for build optimization
- Service Workers for offline functionality
- Web Vitals monitoring

### Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── ui/              # Base UI components (Button, Input, Card)
│   ├── layout/          # Layout components (Header, Footer, Sidebar)
│   ├── forms/           # Form components (SearchForm, FilterForm)
│   └── job/             # Job-specific components (JobCard, JobList)
├── hooks/               # Custom React hooks
│   ├── useIntersectionObserver.ts
│   ├── useDebounce.ts
│   ├── useScroll.ts
│   └── useLocalStorage.ts
├── pages/               # Page components
├── services/            # API services and utilities
├── stores/              # State management
├── styles/              # Global styles and Tailwind config
└── utils/               # Utility functions
```

## 🎨 Design System Implementation

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        sarkari: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
        },
        danger: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      screens: {
        'xs': '475px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

### Component Library Base

```typescript
// src/components/ui/Button.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
  {
    variants: {
      variant: {
        primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
        secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500',
        success: 'bg-success-600 text-white hover:bg-success-700 focus:ring-success-500',
        warning: 'bg-warning-600 text-white hover:bg-warning-700 focus:ring-warning-500',
        danger: 'bg-danger-600 text-white hover:bg-danger-700 focus:ring-danger-500',
        outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-primary-500',
        ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-sm',
        lg: 'px-6 py-3 text-base',
        xl: 'px-8 py-4 text-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Loading...
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);
```

## 📱 Core Component Implementation

### 1. Premium Header Component

```typescript
// src/components/layout/Header.tsx
import React, { useState, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Bars3Icon, XMarkIcon, BellIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useScroll } from '@/hooks/useScroll';
import { cn } from '@/utils/cn';

const navigation = [
  { name: 'Latest Jobs', href: '/jobs/latest' },
  { name: 'Admit Card', href: '/jobs/admit-card' },
  { name: 'Answer Key', href: '/jobs/answer-key' },
  { name: 'Result', href: '/jobs/result' },
  { name: 'Categories', href: '/categories' },
];

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const { scrollY, scrollDirection } = useScroll();

  const isScrolled = scrollY > 10;
  const shouldHideHeader = scrollDirection === 'down' && scrollY > 100;

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        isScrolled ? 'bg-white/80 backdrop-blur-md shadow-lg' : 'bg-white',
        shouldHideHeader ? '-translate-y-full' : 'translate-y-0'
      )}
    >
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" aria-label="Top">
        <div className="flex w-full items-center justify-between border-b border-primary-500 py-4 lg:border-none">
          {/* Logo */}
          <div className="flex items-center">
            <a href="/" className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary-600 to-sarkari-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">SB</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold text-gray-900">SarkariBot</h1>
                <p className="text-xs text-gray-500">Government Job Portal</p>
              </div>
            </a>
          </div>

          {/* Desktop Navigation */}
          <div className="ml-10 hidden space-x-8 lg:block">
            {navigation.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="text-base font-medium text-gray-500 hover:text-primary-600 transition-colors duration-200"
              >
                {link.name}
              </a>
            ))}
          </div>

          {/* Search and Actions */}
          <div className="ml-6 flex items-center space-x-4">
            {/* Search Button */}
            <button
              onClick={() => setSearchOpen(true)}
              className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-primary-600 transition-colors duration-200"
              aria-label="Search jobs"
            >
              <MagnifyingGlassIcon className="h-5 w-5" />
            </button>

            {/* Notifications */}
            <button
              className="relative rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-primary-600 transition-colors duration-200"
              aria-label="View notifications"
            >
              <BellIcon className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-danger-500 animate-pulse" />
            </button>

            {/* Mobile menu button */}
            <button
              type="button"
              className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 lg:hidden"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open main menu"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        <Transition show={mobileMenuOpen}>
          <Dialog onClose={setMobileMenuOpen} className="lg:hidden">
            <Transition.Child
              enter="duration-150 ease-out"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="duration-150 ease-in"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <div className="fixed inset-0 z-50 bg-black/25" />
            </Transition.Child>

            <Transition.Child
              enter="duration-150 ease-out"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="duration-150 ease-in"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="fixed inset-y-0 left-0 z-50 w-full overflow-y-auto bg-white px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10">
                <div className="flex items-center justify-between">
                  <a href="/" className="-m-1.5 p-1.5">
                    <span className="text-lg font-bold text-primary-600">SarkariBot</span>
                  </a>
                  <button
                    type="button"
                    className="-m-2.5 rounded-md p-2.5 text-gray-700"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>
                <div className="mt-6 flow-root">
                  <div className="-my-6 divide-y divide-gray-500/10">
                    <div className="space-y-2 py-6">
                      {navigation.map((item) => (
                        <a
                          key={item.name}
                          href={item.href}
                          className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50"
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          {item.name}
                        </a>
                      ))}
                    </div>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </Dialog>
        </Transition>
      </nav>
    </header>
  );
}
```

### 2. Job Card Component

```typescript
// src/components/job/JobCard.tsx
import React, { useState } from 'react';
import { HeartIcon, ShareIcon, CalendarIcon, MapPinIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/utils/cn';
import { Button } from '@/components/ui/Button';

interface JobCardProps {
  job: {
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
    isSaved?: boolean;
    category: string;
    applyLink?: string;
    slug: string;
  };
  onSave?: (jobId: string) => void;
  onShare?: (job: any) => void;
}

export default function JobCard({ job, onSave, onShare }: JobCardProps) {
  const [isSaved, setIsSaved] = useState(job.isSaved || false);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleSave = () => {
    setIsAnimating(true);
    setIsSaved(!isSaved);
    onSave?.(job.id);
    setTimeout(() => setIsAnimating(false), 300);
  };

  const handleShare = () => {
    onShare?.(job);
  };

  const daysUntilDeadline = Math.ceil(
    (new Date(job.lastDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  );

  const isUrgent = daysUntilDeadline <= 3 && daysUntilDeadline > 0;
  const isExpired = daysUntilDeadline < 0;

  return (
    <div className="group relative bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
      {/* Status Indicators */}
      <div className="absolute top-4 left-4 flex flex-wrap gap-2">
        {job.isNew && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
            New
          </span>
        )}
        {job.isHot && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-danger-100 text-danger-800 animate-pulse">
            Hot
          </span>
        )}
        {isUrgent && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-100 text-warning-800">
            Closing Soon
          </span>
        )}
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        className="absolute top-4 right-4 p-2 rounded-full bg-white shadow-sm border border-gray-200 hover:bg-gray-50 transition-colors duration-200"
        aria-label={isSaved ? 'Remove from saved jobs' : 'Save job'}
      >
        {isSaved ? (
          <HeartSolidIcon className={cn("h-5 w-5 text-danger-500", isAnimating && "animate-scale-in")} />
        ) : (
          <HeartIcon className="h-5 w-5 text-gray-400 group-hover:text-danger-500 transition-colors duration-200" />
        )}
      </button>

      <div className="p-6">
        {/* Job Title & Organization */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 group-hover:text-primary-600 transition-colors duration-200">
            <a href={`/jobs/${job.slug}`} className="hover:underline">
              {job.title}
            </a>
          </h3>
          <div className="flex items-center mt-2 text-sm text-gray-600">
            <BuildingOfficeIcon className="h-4 w-4 mr-1.5 flex-shrink-0" />
            <span className="truncate">{job.organization}</span>
          </div>
        </div>

        {/* Job Details */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-sm text-gray-600">
            <MapPinIcon className="h-4 w-4 mr-1.5 flex-shrink-0" />
            <span>{job.location}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              <strong className="text-gray-900">{job.totalPosts}</strong> Posts
            </span>
            <span className="text-gray-600">
              {job.qualification}
            </span>
          </div>
        </div>

        {/* Deadline */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center text-sm">
            <CalendarIcon className="h-4 w-4 mr-1.5 flex-shrink-0 text-gray-400" />
            <span className="text-gray-600">
              Last Date: {new Date(job.lastDate).toLocaleDateString()}
            </span>
          </div>
          {!isExpired && (
            <span className={cn(
              "text-xs font-medium px-2 py-1 rounded-full",
              isUrgent ? "bg-warning-100 text-warning-800" : "bg-gray-100 text-gray-700"
            )}>
              {daysUntilDeadline} days left
            </span>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleShare}
              className="flex items-center space-x-1"
            >
              <ShareIcon className="h-4 w-4" />
              <span>Share</span>
            </Button>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="secondary"
              size="sm"
              asChild
            >
              <a href={`/jobs/${job.slug}`}>View Details</a>
            </Button>

            {job.applyLink && !isExpired && (
              <Button size="sm" asChild>
                <a
                  href={job.applyLink}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Apply Now
                </a>
              </Button>
            )}
          </div>
        </div>

        {/* Time since published */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            Published {formatDistanceToNow(new Date(job.publishedDate), { addSuffix: true })}
          </p>
        </div>
      </div>
    </div>
  );
}
```

### 3. Performance Hooks

```typescript
// src/hooks/useIntersectionObserver.ts
import { useEffect, useRef, useState } from 'react';

interface UseIntersectionObserverProps {
  threshold?: number;
  root?: Element | null;
  rootMargin?: string;
  freezeOnceVisible?: boolean;
}

export function useIntersectionObserver({
  threshold = 0,
  root = null,
  rootMargin = '0%',
  freezeOnceVisible = false,
}: UseIntersectionObserverProps = {}) {
  const [entry, setEntry] = useState<IntersectionObserverEntry>();
  const [node, setNode] = useState<Element | null>(null);
  const observer = useRef<IntersectionObserver | null>(null);

  const frozen = entry?.isIntersecting && freezeOnceVisible;

  const updateEntry = ([entry]: IntersectionObserverEntry[]): void => {
    setEntry(entry);
  };

  useEffect(() => {
    const hasIOSupport = !!window.IntersectionObserver;

    if (!hasIOSupport || frozen || !node) return;

    const observerParams = { threshold, root, rootMargin };
    const isEqual = observer.current?.root === root &&
      observer.current?.rootMargin === rootMargin &&
      observer.current?.thresholds[0] === threshold;

    if (observer.current && isEqual) return;

    if (observer.current) {
      observer.current.disconnect();
    }

    observer.current = new window.IntersectionObserver(updateEntry, observerParams);
    observer.current.observe(node);

    return () => observer.current?.disconnect();
  }, [node, threshold, root, rootMargin, frozen]);

  const disconnect = () => observer.current?.disconnect();

  return { setNode, entry, disconnect };
}

// Usage example
export function useInfiniteScroll() {
  const { setNode, entry } = useIntersectionObserver({
    threshold: 0.1,
    rootMargin: '100px',
  });

  return {
    setTriggerRef: setNode,
    isVisible: !!entry?.isIntersecting,
  };
}
```

```typescript
// src/hooks/useScroll.ts
import { useEffect, useState } from 'react';
import { useDebounce } from './useDebounce';

export function useScroll() {
  const [scrollY, setScrollY] = useState(0);
  const [scrollDirection, setScrollDirection] = useState<'up' | 'down'>('up');
  const [lastScrollY, setLastScrollY] = useState(0);

  const debouncedScrollY = useDebounce(scrollY, 10);

  useEffect(() => {
    const updateScrollY = () => {
      const currentScrollY = window.scrollY;

      setScrollDirection(currentScrollY > lastScrollY ? 'down' : 'up');
      setScrollY(currentScrollY);
      setLastScrollY(currentScrollY);
    };

    const handleScroll = () => requestAnimationFrame(updateScrollY);

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  return {
    scrollY: debouncedScrollY,
    scrollDirection,
  };
}
```

```typescript
// src/hooks/useDebounce.ts
import { useEffect, useState } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

## 🚀 Implementation Phases

### Phase 1: Foundation Setup (Days 1-3)

**Day 1: Project Setup**

```bash
# Create new React project with TypeScript
npx create-react-app sarkaribot-frontend --template typescript
cd sarkaribot-frontend

# Install essential dependencies
npm install @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio
npm install @headlessui/react @heroicons/react
npm install clsx class-variance-authority
npm install framer-motion date-fns
npm install @tanstack/react-query zustand
npm install react-router-dom react-helmet-async

# Install development dependencies
npm install -D @types/react-router-dom prettier eslint-config-prettier
```

**Day 2: Design System Setup**

- Configure Tailwind CSS with custom design tokens
- Set up component library structure
- Create base components (Button, Input, Card)
- Implement responsive grid system

**Day 3: Routing & Layout**

- Set up React Router
- Create main layout structure
- Implement basic page components
- Add global styles and fonts

### Phase 2: Core Components (Days 4-7)

**Day 4: Header Component**

- Implement sticky navigation with scroll behavior
- Add mobile hamburger menu
- Integrate search functionality
- Add notification system

**Day 5: Job Card Component**

- Create responsive job card design
- Implement save/bookmark functionality
- Add sharing capabilities
- Include micro-interactions

**Day 6: Job List & Infinite Scroll**

- Implement job listing container
- Add infinite scroll with intersection observer
- Create loading states and skeletons
- Add filtering and sorting

**Day 7: Search & Filter System**

- Build advanced search component
- Implement filter sidebar
- Add search suggestions
- Create filter chips

### Phase 3: Advanced Features (Days 8-12)

**Day 8: Homepage Layout**

- Create hero section with statistics
- Implement category grid
- Add trending jobs section
- Build call-to-action areas

**Day 9: Job Detail Page**

- Design comprehensive job detail layout
- Add application timeline
- Implement related jobs section
- Include social sharing

**Day 10: Performance Optimization**

- Implement code splitting
- Add service worker
- Optimize images and assets
- Set up performance monitoring

**Day 11: PWA Features**

- Add offline functionality
- Implement push notifications
- Create app manifest
- Add installation prompts

**Day 12: Accessibility & Testing**

- Audit accessibility compliance
- Add keyboard navigation
- Implement focus management
- Create automated tests

### Phase 4: Polish & Deployment (Days 13-15)

**Day 13: Cross-browser Testing**

- Test on multiple browsers
- Fix compatibility issues
- Optimize for different screen sizes
- Validate responsive behavior

**Day 14: Performance Audits**

- Run Lighthouse audits
- Optimize Core Web Vitals
- Minimize bundle sizes
- Implement caching strategies

**Day 15: Final Polish**

- Add error boundaries
- Implement loading states
- Fine-tune animations
- Prepare for production deployment

## 📊 Success Metrics & Monitoring

### Performance Targets

- Lighthouse Performance Score: >90
- First Contentful Paint: <1.8s
- Largest Contentful Paint: <2.5s
- Cumulative Layout Shift: <0.1
- Time to Interactive: <3.8s

### User Experience Metrics

- Mobile usability score: >95
- Accessibility score: >95
- Cross-browser compatibility: 100%
- Mobile conversion rate: >2.5%

### Monitoring Setup

```typescript
// src/utils/webVitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

export function reportWebVitals(onPerfEntry?: (metric: any) => void) {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    getCLS(onPerfEntry);
    getFID(onPerfEntry);
    getFCP(onPerfEntry);
    getLCP(onPerfEntry);
    getTTFB(onPerfEntry);
  }
}

// Analytics integration
export function sendToAnalytics(metric: any) {
  const body = JSON.stringify(metric);
  const url = '/api/analytics';

  // Use `navigator.sendBeacon()` if available, falling back to `fetch()`
  if (navigator.sendBeacon) {
    navigator.sendBeacon(url, body);
  } else {
    fetch(url, { body, method: 'POST', keepalive: true });
  }
}
```

This implementation guide provides a comprehensive roadmap for building a premium Sarkari Result-style job portal that exceeds industry standards in performance, accessibility, and user experience.
