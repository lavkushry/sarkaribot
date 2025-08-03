import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import apiService from '../services/apiService';
import JobCard from '../components/jobs/JobCard';
import FilterSidebar from '../components/jobs/FilterSidebar';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Pagination from '../components/common/Pagination';

const JobsPage = () => {
  const [searchParams] = useSearchParams();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: searchParams.get('status') || 'announced',
    category: searchParams.get('category') || '',
    source: searchParams.get('source') || '',
    search: searchParams.get('q') || '',
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalResults: 0,
  });

  useEffect(() => {
    loadJobs();
  }, [searchParams]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page: pagination.currentPage,
        page_size: 20,
        ...filters,
      };

      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      const response = await apiService.getJobs(params);
      
      setJobs(response.results || []);
      setPagination(prev => ({
        ...prev,
        totalPages: response.total_pages || 1,
        totalResults: response.count || 0,
      }));
    } catch (err) {
      console.error('Failed to load jobs:', err);
      setError('Failed to load jobs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPagination(prev => ({ ...prev, currentPage: 1 }));
  };

  const handlePageChange = (page) => {
    setPagination(prev => ({ ...prev, currentPage: page }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getPageTitle = () => {
    const statusTitles = {
      announced: 'Latest Jobs',
      admit_card: 'Admit Card',
      answer_key: 'Answer Key',
      result: 'Result',
    };
    return statusTitles[filters.status] || 'Government Jobs';
  };

  if (error) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadJobs}
            className="btn btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {getPageTitle()}
        </h1>
        <p className="text-gray-600">
          {pagination.totalResults > 0
            ? `Showing ${pagination.totalResults} government job${pagination.totalResults === 1 ? '' : 's'}`
            : 'No jobs found matching your criteria'
          }
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <FilterSidebar
            filters={filters}
            onFilterChange={handleFilterChange}
          />
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {loading ? (
            <LoadingSpinner />
          ) : jobs.length > 0 ? (
            <>
              {/* Jobs Grid */}
              <div className="grid grid-cols-1 gap-6 mb-8">
                {jobs.map((job) => (
                  <JobCard key={job.id} job={job} variant="detailed" />
                ))}
              </div>

              {/* Pagination */}
              {pagination.totalPages > 1 && (
                <Pagination
                  currentPage={pagination.currentPage}
                  totalPages={pagination.totalPages}
                  onPageChange={handlePageChange}
                />
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl text-gray-400 mb-4">📝</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No jobs found
              </h3>
              <p className="text-gray-600">
                Try adjusting your search criteria or check back later for new postings.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobsPage;
