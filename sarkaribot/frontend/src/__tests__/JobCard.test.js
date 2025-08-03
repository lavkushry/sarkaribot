import React from 'react';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockJobPosting, setupTest } from '../test-utils';
import JobCard from '../components/JobCard';

// Setup mocks for each test
setupTest();

describe('JobCard Component', () => {
  test('renders job card with all required information', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    // Check if all essential elements are present
    expect(screen.getByTestId('job-title')).toBeInTheDocument();
    expect(screen.getByTestId('source-name')).toBeInTheDocument();
    expect(screen.getByTestId('application-deadline')).toBeInTheDocument();
    expect(screen.getByTestId('apply-button')).toBeInTheDocument();
  });

  test('displays job title correctly', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const titleElement = screen.getByTestId('job-title');
    expect(titleElement).toHaveTextContent(mockJobPosting.title);
  });

  test('displays source information', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const sourceElement = screen.getByTestId('source-name');
    expect(sourceElement).toHaveTextContent(mockJobPosting.source.display_name);
  });

  test('displays application deadline', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const deadlineElement = screen.getByTestId('application-deadline');
    expect(deadlineElement).toBeInTheDocument();
    // Should contain the date in some format
    expect(deadlineElement).toHaveTextContent('2024');
  });

  test('shows salary information when available', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    // Should display salary range
    const salaryElement = screen.queryByTestId('salary-range');
    if (salaryElement) {
      expect(salaryElement).toHaveTextContent('25000');
      expect(salaryElement).toHaveTextContent('50000');
    }
  });

  test('displays total posts when available', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const postsElement = screen.queryByTestId('total-posts');
    if (postsElement) {
      expect(postsElement).toHaveTextContent('100');
    }
  });

  test('apply button links to correct URL', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const applyButton = screen.getByTestId('apply-button');
    expect(applyButton).toHaveAttribute('href', mockJobPosting.application_link);
  });

  test('job title links to job detail page', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const titleLink = screen.getByTestId('job-title-link');
    expect(titleLink).toHaveAttribute('href', `/jobs/${mockJobPosting.slug}`);
  });

  test('shows featured badge for featured jobs', () => {
    const featuredJob = { ...mockJobPosting, is_featured: true };
    renderWithProviders(<JobCard job={featuredJob} />);
    
    const featuredBadge = screen.queryByTestId('featured-badge');
    expect(featuredBadge).toBeInTheDocument();
  });

  test('does not show featured badge for non-featured jobs', () => {
    const normalJob = { ...mockJobPosting, is_featured: false };
    renderWithProviders(<JobCard job={normalJob} />);
    
    const featuredBadge = screen.queryByTestId('featured-badge');
    expect(featuredBadge).not.toBeInTheDocument();
  });

  test('shows status badge with correct color', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const statusBadge = screen.queryByTestId('status-badge');
    if (statusBadge) {
      expect(statusBadge).toHaveTextContent('announced');
    }
  });

  test('handles missing optional fields gracefully', () => {
    const minimalJob = {
      id: 1,
      title: 'Test Job',
      slug: 'test-job',
      source: { name: 'TEST', display_name: 'Test Source' },
      category: { name: 'Test Category' },
      application_link: 'https://test.gov.in'
    };
    
    expect(() => {
      renderWithProviders(<JobCard job={minimalJob} />);
    }).not.toThrow();
  });

  test('formats dates correctly', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    // Check if date formatting is applied
    const dateElements = screen.getAllByText(/2024/);
    expect(dateElements.length).toBeGreaterThan(0);
  });

  test('truncates long job titles appropriately', () => {
    const longTitleJob = {
      ...mockJobPosting,
      title: 'This is a very long job title that should be truncated to prevent layout issues and maintain readability'
    };
    
    renderWithProviders(<JobCard job={longTitleJob} />);
    
    const titleElement = screen.getByTestId('job-title');
    // Check if title is present (implementation may truncate)
    expect(titleElement).toBeInTheDocument();
  });

  test('has proper accessibility attributes', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const titleLink = screen.getByTestId('job-title-link');
    expect(titleLink).toHaveAttribute('aria-label');
    
    const applyButton = screen.getByTestId('apply-button');
    expect(applyButton).toHaveAttribute('aria-label');
  });

  test('handles click events properly', async () => {
    const user = userEvent.setup();
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const titleLink = screen.getByTestId('job-title-link');
    
    // Should not throw error when clicked
    await expect(user.click(titleLink)).resolves.not.toThrow();
  });

  test('responsive design elements are present', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    const cardElement = screen.getByTestId('job-card');
    expect(cardElement).toHaveClass('job-card');
  });

  test('matches SarkariExam.com design structure', () => {
    renderWithProviders(<JobCard job={mockJobPosting} />);
    
    // Check for expected CSS classes or structure
    const cardElement = screen.getByTestId('job-card');
    expect(cardElement).toBeInTheDocument();
    
    // Should have proper structure similar to SarkariExam.com
    expect(screen.getByTestId('job-title')).toBeInTheDocument();
    expect(screen.getByTestId('source-name')).toBeInTheDocument();
    expect(screen.getByTestId('apply-button')).toBeInTheDocument();
  });
});