// Test utilities for React Testing Library
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import '@testing-library/jest-dom';

// Create a custom render function that includes providers
export const renderWithProviders = (ui, options = {}) => {
  // Create a new QueryClient for each test
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const AllTheProviders = ({ children }) => {
    return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  return render(ui, { wrapper: AllTheProviders, ...options });
};

// Mock API responses
export const mockJobPosting = {
  id: 1,
  title: 'Software Engineer - Government of India',
  slug: 'software-engineer-govt-india',
  description: 'Join the Government of India as a Software Engineer...',
  source: {
    id: 1,
    name: 'SSC',
    display_name: 'Staff Selection Commission',
    base_url: 'https://ssc.nic.in'
  },
  category: {
    id: 1,
    name: 'Latest Jobs',
    slug: 'latest-jobs'
  },
  application_link: 'https://ssc.nic.in/apply/12345',
  application_end_date: '2024-12-31',
  salary_min: 25000,
  salary_max: 50000,
  total_posts: 100,
  status: 'announced',
  created_at: '2024-01-15T10:00:00Z',
  seo_title: 'Software Engineer Government Job 2024 - Apply Online | SarkariBot',
  seo_description: 'Apply for Software Engineer position in Government of India. Last date: 31 Dec 2024. Check eligibility and apply online.',
  is_featured: true
};

export const mockJobCategory = {
  id: 1,
  name: 'Latest Jobs',
  slug: 'latest-jobs',
  description: 'Latest government job postings',
  job_count: 150,
  is_active: true
};

export const mockGovernmentSource = {
  id: 1,
  name: 'SSC',
  display_name: 'Staff Selection Commission',
  base_url: 'https://ssc.nic.in',
  active: true,
  total_jobs_found: 500,
  stats: {
    jobs_this_month: 25,
    success_rate: 95.5,
    avg_jobs_per_scrape: 12.5
  }
};

// Mock API service
export const mockApiService = {
  getLatestJobs: jest.fn(),
  getJobById: jest.fn(),
  getCategories: jest.fn(),
  searchJobs: jest.fn(),
  getJobsByCategory: jest.fn(),
  getStats: jest.fn(),
  getTrendingJobs: jest.fn(),
  getPopularJobs: jest.fn()
};

// Mock API responses
export const setupApiMocks = () => {
  mockApiService.getLatestJobs.mockResolvedValue({
    results: [mockJobPosting],
    count: 1,
    next: null,
    previous: null
  });

  mockApiService.getJobById.mockResolvedValue(mockJobPosting);

  mockApiService.getCategories.mockResolvedValue([mockJobCategory]);

  mockApiService.searchJobs.mockResolvedValue({
    results: [mockJobPosting],
    count: 1
  });

  mockApiService.getJobsByCategory.mockResolvedValue({
    results: [mockJobPosting],
    count: 1
  });

  mockApiService.getStats.mockResolvedValue({
    total_jobs: 1500,
    jobs_this_week: 45,
    total_sources: 25,
    active_sources: 23
  });

  mockApiService.getTrendingJobs.mockResolvedValue([mockJobPosting]);
  mockApiService.getPopularJobs.mockResolvedValue([mockJobPosting]);
};

// Utility to wait for async operations
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0));

// Custom matchers
export const customMatchers = {
  toBeValidJobCard: (received) => {
    const requiredElements = [
      'job-title',
      'source-name', 
      'application-deadline',
      'apply-button'
    ];

    const missing = requiredElements.filter(
      element => !received.querySelector(`[data-testid="${element}"]`)
    );

    if (missing.length === 0) {
      return {
        message: () => `Expected job card to be invalid`,
        pass: true,
      };
    } else {
      return {
        message: () => `Expected job card to have elements: ${missing.join(', ')}`,
        pass: false,
      };
    }
  }
};

// Setup function for tests
export const setupTest = () => {
  beforeEach(() => {
    setupApiMocks();
    // Clear all mocks before each test
    jest.clearAllMocks();
  });
};

export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';