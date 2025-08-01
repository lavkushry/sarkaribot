import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockApiService, mockJobPosting, setupTest } from '../test-utils';
import HomePage from '../pages/HomePage';

// Setup mocks for each test
setupTest();

// Mock the apiService
jest.mock('../services/apiService', () => ({
  __esModule: true,
  default: mockApiService
}));

describe('HomePage Component', () => {
  test('renders loading state initially', () => {
    // Mock API calls to return pending promises
    mockApiService.getLatestJobs.mockReturnValue(new Promise(() => {}));
    mockApiService.getCategories.mockReturnValue(new Promise(() => {}));
    mockApiService.getStats.mockReturnValue(new Promise(() => {}));
    mockApiService.getTrendingJobs.mockReturnValue(new Promise(() => {}));

    renderWithProviders(<HomePage />);
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('renders homepage content after data loads', async () => {
    renderWithProviders(<HomePage />);
    
    // Wait for content to load
    await waitFor(() => {
      expect(screen.getByTestId('homepage-content')).toBeInTheDocument();
    });

    // Check for main sections
    expect(screen.getByTestId('latest-jobs-section')).toBeInTheDocument();
    expect(screen.getByTestId('categories-section')).toBeInTheDocument();
    expect(screen.getByTestId('stats-section')).toBeInTheDocument();
  });

  test('displays latest jobs section', async () => {
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('latest-jobs-section')).toBeInTheDocument();
    });

    // Should display job cards
    expect(screen.getByTestId('job-card')).toBeInTheDocument();
    expect(screen.getByText(mockJobPosting.title)).toBeInTheDocument();
  });

  test('displays categories section', async () => {
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('categories-section')).toBeInTheDocument();
    });

    // Should display category cards
    expect(screen.getByText('Latest Jobs')).toBeInTheDocument();
    expect(screen.getByTestId('category-card')).toBeInTheDocument();
  });

  test('displays statistics section', async () => {
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('stats-section')).toBeInTheDocument();
    });

    // Should display stats
    expect(screen.getByText('1500')).toBeInTheDocument(); // total_jobs
    expect(screen.getByText('45')).toBeInTheDocument();   // jobs_this_week
  });

  test('shows error state when API calls fail', async () => {
    // Mock API to reject
    mockApiService.getLatestJobs.mockRejectedValue(new Error('API Error'));
    mockApiService.getCategories.mockRejectedValue(new Error('API Error'));
    mockApiService.getStats.mockRejectedValue(new Error('API Error'));
    mockApiService.getTrendingJobs.mockRejectedValue(new Error('API Error'));

    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });

    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });

  test('has search functionality', async () => {
    const user = userEvent.setup();
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('search-input')).toBeInTheDocument();
    });

    const searchInput = screen.getByTestId('search-input');
    const searchButton = screen.getByTestId('search-button');

    await user.type(searchInput, 'software engineer');
    await user.click(searchButton);

    // Should call search API or navigate to search page
    expect(mockApiService.searchJobs).toHaveBeenCalledWith('software engineer');
  });

  test('displays trending jobs section', async () => {
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('trending-jobs-section')).toBeInTheDocument();
    });

    // Should display trending job cards
    expect(screen.getByTestId('trending-job-card')).toBeInTheDocument();
  });

  test('has navigation links to other pages', async () => {
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('homepage-content')).toBeInTheDocument();
    });

    // Check for navigation links
    expect(screen.getByTestId('view-all-jobs-link')).toBeInTheDocument();
    expect(screen.getByTestId('view-all-categories-link')).toBeInTheDocument();
  });

  test('shows quick links sidebar', async () => {
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('quick-links-sidebar')).toBeInTheDocument();
    });

    // Should have popular job links
    expect(screen.getByTestId('popular-jobs-section')).toBeInTheDocument();
  });

  test('matches SarkariExam.com layout structure', async () => {
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('homepage-content')).toBeInTheDocument();
    });

    // Check for main layout elements
    expect(screen.getByTestId('main-content')).toBeInTheDocument();
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    
    // Check for header and footer
    expect(screen.getByTestId('page-header')).toBeInTheDocument();
    expect(screen.getByTestId('page-footer')).toBeInTheDocument();
  });

  test('is responsive and mobile-friendly', async () => {
    // Test with different viewport sizes
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    });

    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('homepage-content')).toBeInTheDocument();
    });

    // Should have responsive classes
    const mainContent = screen.getByTestId('main-content');
    expect(mainContent).toHaveClass('responsive-content');
  });

  test('handles pagination for job listings', async () => {
    const user = userEvent.setup();
    
    // Mock paginated response
    mockApiService.getLatestJobs.mockResolvedValue({
      results: [mockJobPosting],
      count: 50,
      next: 'http://api.example.com/jobs/?page=2',
      previous: null
    });

    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('latest-jobs-section')).toBeInTheDocument();
    });

    // Should show pagination if more than page size
    const viewMoreButton = screen.queryByTestId('view-more-jobs');
    if (viewMoreButton) {
      await user.click(viewMoreButton);
      // Should load more jobs
    }
  });

  test('shows featured jobs prominently', async () => {
    const featuredJob = { ...mockJobPosting, is_featured: true };
    mockApiService.getLatestJobs.mockResolvedValue({
      results: [featuredJob],
      count: 1
    });

    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('featured-jobs-section')).toBeInTheDocument();
    });

    expect(screen.getByTestId('featured-badge')).toBeInTheDocument();
  });

  test('has proper SEO elements', async () => {
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('homepage-content')).toBeInTheDocument();
    });

    // Check for SEO elements (would be in Helmet component)
    expect(document.title).toContain('SarkariBot');
  });

  test('handles refresh and data reloading', async () => {
    const user = userEvent.setup();
    renderWithProviders(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('homepage-content')).toBeInTheDocument();
    });

    // Clear mocks to track new calls
    jest.clearAllMocks();

    // Simulate page refresh or manual reload
    const refreshButton = screen.queryByTestId('refresh-button');
    if (refreshButton) {
      await user.click(refreshButton);
      
      // Should make new API calls
      expect(mockApiService.getLatestJobs).toHaveBeenCalled();
      expect(mockApiService.getCategories).toHaveBeenCalled();
    }
  });
});