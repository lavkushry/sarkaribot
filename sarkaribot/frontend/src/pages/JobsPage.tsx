/**
 * JobsPage component for listing jobs
 * Supports filtering by status and other criteria
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { JobPosting, JobFilters, apiService, getJobStatusLabel } from '../services/api.ts';
import JobCard from '../components/JobCard.tsx';

const PageContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

const PageHeader = styled.div`
  margin-bottom: 30px;
`;

const PageTitle = styled.h1`
  font-size: 28px;
  color: #1e3c72;
  margin-bottom: 10px;
  font-weight: 600;
`;

const PageDescription = styled.p`
  color: #666;
  font-size: 16px;
  line-height: 1.5;
`;

const FiltersContainer = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const FiltersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
`;

const FilterGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const FilterLabel = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: #333;
`;

const FilterSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  
  &:focus {
    outline: none;
    border-color: #1e3c72;
  }
`;

const FilterInput = styled.input`
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #1e3c72;
  }
`;

const FilterActions = styled.div`
  display: flex;
  gap: 10px;
  justify-content: flex-end;
`;

const FilterButton = styled.button`
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  
  &.primary {
    background: #1e3c72;
    color: white;
    border: none;
    
    &:hover {
      background: #2a5298;
    }
  }
  
  &.secondary {
    background: #f8f9fa;
    color: #333;
    border: 1px solid #e0e0e0;
    
    &:hover {
      background: #e9ecef;
    }
  }
`;

const ResultsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const ResultsCount = styled.div`
  font-size: 14px;
  color: #666;
`;

const SortSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  background: white;
`;

const JobsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 16px;
  color: #666;
`;

const ErrorMessage = styled.div`
  background: #f8d7da;
  color: #721c24;
  padding: 15px;
  border-radius: 4px;
  margin: 20px 0;
  text-align: center;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #666;
  
  h3 {
    margin-bottom: 15px;
    color: #333;
    font-size: 24px;
  }
  
  p {
    margin: 0;
    line-height: 1.6;
    font-size: 16px;
  }
`;

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 30px;
`;

const PaginationButton = styled.button<{ active?: boolean }>`
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  background: ${props => props.active ? '#1e3c72' : 'white'};
  color: ${props => props.active ? 'white' : '#333'};
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover:not(:disabled) {
    background: ${props => props.active ? '#1e3c72' : '#f8f9fa'};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

interface JobsPageProps {
  status?: string;
  filter?: string;
}

const JobsPage: React.FC<JobsPageProps> = ({ status, filter }) => {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();

  // Filter state
  const [filters, setFilters] = useState<JobFilters>({
    status: status || '',
    search: searchParams.get('search') || '',
    location: searchParams.get('location') || '',
    qualification: searchParams.get('qualification') || '',
    ordering: '-created_at',
    page: 1,
    page_size: 20,
  });

  useEffect(() => {
    loadJobs();
  }, [filters, status, filter]);

  useEffect(() => {
    // Apply URL-based filters
    const newFilters = { ...filters };
    
    if (status) newFilters.status = status;
    if (filter) {
      switch (filter) {
        case 'deadline_soon':
          newFilters.deadline_soon = true;
          break;
        case 'high_posts':
          newFilters.high_posts = true;
          break;
        case 'free_application':
          newFilters.free_application = true;
          break;
      }
    }
    
    setFilters(newFilters);
  }, [status, filter]);

  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiService.getJobs(filters);
      setJobs(response.results);
      setTotalCount(response.count);
    } catch (err) {
      setError('Failed to load jobs. Please try again later.');
      console.error('Error loading jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: keyof JobFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1, // Reset to first page when filters change
    }));
    setCurrentPage(1);
  };

  const handleApplyFilters = () => {
    loadJobs();
  };

  const handleClearFilters = () => {
    setFilters({
      status: status || '',
      ordering: '-created_at',
      page: 1,
      page_size: 20,
    });
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    setFilters(prev => ({ ...prev, page }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getPageTitle = () => {
    if (status) return getJobStatusLabel(status);
    if (filter) {
      switch (filter) {
        case 'deadline_soon': return 'Jobs with Deadline Soon';
        case 'high_posts': return 'High Posts Jobs';
        case 'free_application': return 'Free Application Jobs';
        default: return 'Government Jobs';
      }
    }
    return 'All Government Jobs';
  };

  const getPageDescription = () => {
    if (status) {
      return `Browse all ${getJobStatusLabel(status).toLowerCase()} from central and state government departments.`;
    }
    return 'Find the latest government job opportunities from various departments and organizations.';
  };

  const totalPages = Math.ceil(totalCount / (filters.page_size || 20));

  return (
    <PageContainer>
      <PageHeader>
        <PageTitle>{getPageTitle()}</PageTitle>
        <PageDescription>{getPageDescription()}</PageDescription>
      </PageHeader>

      {/* Filters */}
      <FiltersContainer>
        <FiltersGrid>
          <FilterGroup>
            <FilterLabel>Search</FilterLabel>
            <FilterInput
              type="text"
              placeholder="Search jobs..."
              value={filters.search || ''}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </FilterGroup>

          <FilterGroup>
            <FilterLabel>Location</FilterLabel>
            <FilterInput
              type="text"
              placeholder="Enter location"
              value={filters.location || ''}
              onChange={(e) => handleFilterChange('location', e.target.value)}
            />
          </FilterGroup>

          <FilterGroup>
            <FilterLabel>Qualification</FilterLabel>
            <FilterInput
              type="text"
              placeholder="Enter qualification"
              value={filters.qualification || ''}
              onChange={(e) => handleFilterChange('qualification', e.target.value)}
            />
          </FilterGroup>

          <FilterGroup>
            <FilterLabel>Sort By</FilterLabel>
            <FilterSelect
              value={filters.ordering || '-created_at'}
              onChange={(e) => handleFilterChange('ordering', e.target.value)}
            >
              <option value="-created_at">Latest First</option>
              <option value="created_at">Oldest First</option>
              <option value="-total_posts">High Posts First</option>
              <option value="application_end_date">Deadline</option>
            </FilterSelect>
          </FilterGroup>
        </FiltersGrid>

        <FilterActions>
          <FilterButton className="secondary" onClick={handleClearFilters}>
            Clear Filters
          </FilterButton>
          <FilterButton className="primary" onClick={handleApplyFilters}>
            Apply Filters
          </FilterButton>
        </FilterActions>
      </FiltersContainer>

      {/* Results */}
      <ResultsContainer>
        <ResultsHeader>
          <ResultsCount>
            {loading ? 'Loading...' : `${totalCount.toLocaleString()} jobs found`}
          </ResultsCount>
        </ResultsHeader>

        {loading && <LoadingSpinner>🔄 Loading jobs...</LoadingSpinner>}
        
        {error && <ErrorMessage>{error}</ErrorMessage>}

        {!loading && !error && (
          <>
            {jobs.length > 0 ? (
              <JobsList>
                {jobs.map((job) => (
                  <JobCard 
                    key={job.id} 
                    job={job} 
                    showDescription={true}
                  />
                ))}
              </JobsList>
            ) : (
              <EmptyState>
                <h3>No jobs found</h3>
                <p>
                  No jobs match your current filters. Try adjusting your search criteria 
                  or clearing the filters to see more results.
                </p>
              </EmptyState>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <Pagination>
                <PaginationButton
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </PaginationButton>

                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const page = i + 1;
                  return (
                    <PaginationButton
                      key={page}
                      active={page === currentPage}
                      onClick={() => handlePageChange(page)}
                    >
                      {page}
                    </PaginationButton>
                  );
                })}

                <PaginationButton
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                </PaginationButton>
              </Pagination>
            )}
          </>
        )}
      </ResultsContainer>
    </PageContainer>
  );
};

export default JobsPage;
