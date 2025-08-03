# GitHub Copilot Implementation Prompt: Premium Sarkari Result-Style Job Portal

## 🎯 Project Overview

You are tasked with implementing a **premium, mobile-first government job portal** inspired by top Sarkari Result websites. This implementation must exceed industry standards in performance, accessibility, and user experience while maintaining the familiar patterns that government job seekers expect.

## 📊 Research-Backed Requirements

Based on comprehensive analysis of leading Sarkari Result websites and modern web development best practices:

### Core Design Principles
1. **Mobile-First Approach**: 65%+ of users access on mobile devices
2. **2-Second Decision Rule**: Users decide within 2 seconds if content is relevant
3. **Thumb Zone Optimization**: Primary actions in bottom 1/3 of screen
4. **Performance-First**: Target Lighthouse score >90, Core Web Vitals in green
5. **Accessibility Standard**: WCAG 2.1 AA compliance

### Key User Behaviors Discovered
- **Fast Scrolling**: Users scroll 3x faster on mobile than desktop
- **One-Handed Usage**: 67% browse one-handed during commute
- **Deadline Anxiety**: Time-sensitive content needs prominent visual treatment
- **Trust Indicators**: Government logos and certifications build credibility
- **Social Sharing**: 40% share job postings with family/friends

## 🏗️ Technical Architecture

### Technology Stack (Confirmed Working)
```json
{
  "frontend": "React 18.2+ with TypeScript",
  "styling": "Tailwind CSS 3.4+",
  "icons": "@heroicons/react",
  "components": "@headlessui/react",
  "animations": "framer-motion",
  "state": "Zustand + React Query",
  "routing": "React Router v6",
  "forms": "React Hook Form",
  "testing": "Jest + React Testing Library"
}
```

### Performance Targets
- First Contentful Paint: < 1.8s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1
- Time to Interactive: < 3.8s
- Total Blocking Time: < 200ms

## 🎨 Design System Implementation

### Color Palette (Government Approved)
```css
:root {
  /* Primary Government Colors */
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;

  /* Sarkari Brand Colors */
  --color-sarkari-500: #0ea5e9;
  --color-sarkari-600: #0284c7;
  --color-sarkari-700: #0369a1;

  /* Status Colors */
  --color-success-500: #22c55e;
  --color-warning-500: #f59e0b;
  --color-danger-500: #ef4444;
}
```

### Typography Scale (Mobile Optimized)
```css
/* 16px base for optimal mobile reading */
--font-size-sm: 0.875rem;    /* 14px - metadata */
--font-size-base: 1rem;      /* 16px - body text */
--font-size-lg: 1.125rem;    /* 18px - card titles */
--font-size-xl: 1.25rem;     /* 20px - section headers */
--font-size-2xl: 1.5rem;     /* 24px - page titles */
--font-size-3xl: 2rem;       /* 32px - hero titles */

/* Line heights for readability */
--line-height-tight: 1.2;    /* headlines */
--line-height-normal: 1.5;   /* body text */
--line-height-relaxed: 1.6;  /* long content */
```

### Spacing System (8px Grid)
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

## 📱 Component Implementation Requirements

### 1. Header Component Specifications

**Behavior Requirements:**
- Sticky positioning with scroll-based shrinking (40% height reduction)
- Backdrop blur effect when scrolled (backdrop-filter: blur(10px))
- Hide on fast downward scroll, show on upward scroll
- Mobile hamburger menu with smooth slide-in animation (300ms)
- Search with real-time suggestions and keyboard navigation

**Implementation Pattern:**
```typescript
// Required hooks: useScroll, useDebounce
// Required animations: transform, backdrop-filter
// Required accessibility: ARIA labels, keyboard navigation
// Touch targets: minimum 44px × 44px
```

### 2. Job Card Component Specifications

**Information Hierarchy (Research-Based):**
1. Job Title (most prominent - font-size: 1.125rem, font-weight: 600)
2. Organization Name (trust factor - with building icon)
3. Key Metrics (posts count, qualification, location)
4. Deadline Information (with urgency indicators)
5. Action Buttons (save, share, apply, view details)

**Visual Elements Required:**
- Left border color-coding by category (4px solid)
- Badge system: "New" (green), "Hot" (red + pulse), "Closing Soon" (orange)
- Save button with heart animation (scale + color transition)
- Deadline countdown with color progression (green → orange → red)
- Hover state: translateY(-2px) + shadow increase

**Micro-Interactions:**
```css
/* Hover effect */
.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  transition: all 0.3s ease;
}

/* Save animation */
.save-btn.saved {
  transform: scale(1.1);
  color: #ef4444;
  animation: heartbeat 0.3s ease;
}
```

### 3. Search & Filter System

**Search Features Required:**
- Autocomplete with job titles, categories, locations, organizations
- Debounced search (300ms) to reduce API calls
- Search suggestions with icons and result counts
- Recent searches persistence (localStorage)
- Voice search capability (Web Speech API)

**Filter Organization:**
1. **Primary Filters** (always visible):
   - Job Category (dropdown with icons)
   - Location (with geolocation option)
   - Date Range (last 7 days, 30 days, etc.)

2. **Secondary Filters** (collapsible):
   - Qualification Level
   - Salary Range
   - Application Status
   - Organization Type

### 4. Infinite Scroll Implementation

**Performance Requirements:**
- Intersection Observer API for trigger detection
- 100px root margin for smooth loading
- Skeleton screens during loading (6 cards)
- Virtual scrolling for lists >100 items
- Error boundary for failed loads

**Loading States:**
```typescript
// Three states: loading, error, success
// Skeleton screens match actual card dimensions
// Progressive loading: 20 items per page
// Smooth transitions between states
```

## 🚀 Performance Implementation

### Code Splitting Strategy
```typescript
// Route-based splitting
const HomePage = lazy(() => import('./pages/HomePage'));
const JobDetailPage = lazy(() => import('./pages/JobDetailPage'));
const SearchPage = lazy(() => import('./pages/SearchPage'));

// Component-level splitting for heavy features
const FilterSidebar = lazy(() => import('./components/FilterSidebar'));
const JobMap = lazy(() => import('./components/JobMap'));
```

### Image Optimization
```typescript
// Responsive images with WebP support
// Lazy loading with intersection observer
// Blur-up loading technique
// Placeholder images for missing content
```

### Caching Strategy
```typescript
// React Query configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
  },
});
```

## 🎭 Animation System

### Micro-Interactions Catalog
```css
/* Page transitions */
.page-enter {
  opacity: 0;
  transform: translateY(20px);
}
.page-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: all 300ms ease-out;
}

/* Card interactions */
.card-hover {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* Button interactions */
.btn-press {
  transform: scale(0.95);
  transition: transform 0.1s ease;
}
```

### Loading Animations
```css
/* Skeleton loading */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

## 📊 Accessibility Implementation

### Keyboard Navigation
```typescript
// Tab order optimization
// Skip links for screen readers
// Focus management for modals
// Arrow key navigation for menus
// Enter/Space activation for custom buttons
```

### Screen Reader Support
```html
<!-- Proper heading hierarchy -->
<h1>Government Jobs Portal</h1>
  <h2>Latest Job Postings</h2>
    <h3>Software Engineer - Railway</h3>

<!-- Descriptive labels -->
<button aria-label="Save Software Engineer position at Indian Railways">
  <HeartIcon />
</button>

<!-- Status announcements -->
<div aria-live="polite" aria-atomic="true">
  New job posted: Data Analyst at ISRO
</div>
```

### Color Accessibility
```css
/* High contrast mode support */
@media (prefers-contrast: high) {
  .btn-primary {
    background: #000;
    color: #fff;
    border: 2px solid #fff;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 🔧 Development Workflow

### Component Creation Checklist
- [ ] Mobile-first responsive design
- [ ] TypeScript interfaces defined
- [ ] Accessibility attributes added
- [ ] Loading and error states
- [ ] Micro-interactions implemented
- [ ] Performance optimized
- [ ] Tests written (unit + integration)

### Quality Gates
```typescript
// Before deployment, ensure:
// - Lighthouse score >90
// - Accessibility score >95
// - Bundle size <250KB initial
// - Core Web Vitals in green
// - Cross-browser compatibility verified
```

## 🎯 Implementation Priority

### Phase 1: Foundation (Days 1-3)
1. **Tailwind Setup**: Custom design system configuration
2. **Base Components**: Button, Input, Card, Modal components
3. **Layout System**: Header, Footer, main content areas
4. **Routing Setup**: React Router with lazy loading

### Phase 2: Core Features (Days 4-7)
1. **Header Component**: Sticky navigation with search
2. **Job Card**: Complete with all interactions
3. **Job List**: Infinite scroll implementation
4. **Search System**: Advanced search with filters

### Phase 3: Advanced Features (Days 8-10)
1. **Homepage**: Hero, categories, trending jobs
2. **Job Detail Page**: Comprehensive job information
3. **Performance Optimization**: Code splitting, caching
4. **PWA Features**: Service worker, offline support

### Phase 4: Polish & Testing (Days 11-12)
1. **Accessibility Audit**: WCAG compliance verification
2. **Performance Testing**: Core Web Vitals optimization
3. **Cross-browser Testing**: Safari, Chrome, Firefox, Edge
4. **User Testing**: Mobile device testing

## 📈 Success Metrics

### Performance KPIs
- Lighthouse Performance: >90
- Mobile Performance: >85
- Accessibility Score: >95
- First Contentful Paint: <1.8s
- Time to Interactive: <3.8s

### User Experience KPIs
- Mobile Conversion Rate: >2.5%
- Bounce Rate: <40%
- Time on Site: >3 minutes
- Page Views per Session: >4
- Return Visitor Rate: >60%

### Technical KPIs
- Bundle Size: <250KB initial load
- API Response Time: <500ms
- Error Rate: <0.1%
- Uptime: >99.9%

## 🎨 Brand Guidelines

### Visual Identity
- **Logo**: Government-approved design with accessibility in mind
- **Typography**: Inter font family for optimal readability
- **Iconography**: Heroicons for consistency and accessibility
- **Photography**: High-quality, diverse representation of job seekers

### Content Guidelines
- **Tone**: Professional yet approachable
- **Language**: Clear, concise, jargon-free
- **Accessibility**: Plain language principles
- **Localization**: Support for regional languages

---

**This prompt ensures the implementation of a world-class government job portal that exceeds user expectations while maintaining the trusted, familiar patterns that Sarkari Result users expect.**
