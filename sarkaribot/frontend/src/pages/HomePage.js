import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';
import './HomePage.css';

const HomePage = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    latestJobs: [],
    categories: [],
    stats: {},
    trendingJobs: []
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadHomePageData = async () => {
      try {
        setLoading(true);
        
        const [latestJobs, categories, stats, trendingJobs] = await Promise.all([
          apiService.getLatestJobs(),
          apiService.getCategories(),
          apiService.getStats(),
          apiService.getTrendingJobs()
        ]);

        setData({
          latestJobs: latestJobs.results || latestJobs,
          categories: categories.results || categories,
          stats: stats,
          trendingJobs: trendingJobs.results || trendingJobs
        });
      } catch (err) {
        console.error('Homepage data loading failed:', err);
        setError('Failed to load homepage data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadHomePageData();
  }, []);

  if (loading) {
    return (
      <div className="homepage-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading SarkariBot...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="homepage-error">
        <div className="error-message">
          <h2>Oops! Something went wrong</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1>SarkariBot - Government Jobs Portal</h1>
          <p>Find the latest government job notifications, admit cards, answer keys, and results</p>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">{data.stats.total_jobs || 0}</span>
              <span className="stat-label">Total Jobs</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{data.stats.active_jobs || 0}</span>
              <span className="stat-label">Active Jobs</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{data.stats.new_jobs_today || 0}</span>
              <span className="stat-label">New Today</span>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="categories-section">
        <div className="container">
          <h2>Job Categories</h2>
          <div className="categories-grid">
            {data.categories.slice(0, 8).map((category) => (
              <CategoryCard 
                key={category.id} 
                category={category}
                jobCount={data.stats.jobs_by_category?.[category.slug]?.count || 0}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Latest Jobs Section */}
      <section className="latest-jobs-section">
        <div className="container">
          <h2>Latest Government Jobs</h2>
          <div className="jobs-grid">
            {data.latestJobs.slice(0, 6).map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
          <div className="section-footer">
            <a href="/jobs" className="view-all-btn">View All Jobs →</a>
          </div>
        </div>
      </section>

      {/* Trending Jobs Section */}
      <section className="trending-jobs-section">
        <div className="container">
          <h2>Trending Jobs</h2>
          <div className="jobs-list">
            {data.trendingJobs.slice(0, 5).map((job) => (
              <TrendingJobItem key={job.id} job={job} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

const CategoryCard = ({ category, jobCount }) => (
  <div className="category-card">
    <a href={`/category/${category.slug}`}>
      <h3>{category.name}</h3>
      <p>{category.description}</p>
      <span className="job-count">{jobCount} Jobs</span>
    </a>
  </div>
);

const JobCard = ({ job }) => (
  <div className="job-card">
    <div className="job-header">
      <h3>
        <a href={`/jobs/${job.slug}`}>{job.title}</a>
      </h3>
      {job.is_new && <span className="new-badge">New</span>}
    </div>
    <div className="job-meta">
      <span className="source">{job.source_name}</span>
      <span className="posts">{job.total_posts} Posts</span>
      <span className="category">{job.category_name}</span>
    </div>
    <div className="job-details">
      <p className="qualification">Qualification: {job.qualification}</p>
      {job.application_end_date && (
        <p className="deadline">
          Last Date: {new Date(job.application_end_date).toLocaleDateString()}
          {job.days_remaining > 0 && (
            <span className="days-left"> ({job.days_remaining} days left)</span>
          )}
        </p>
      )}
    </div>
    <div className="job-actions">
      <a href={`/jobs/${job.slug}`} className="details-btn">View Details</a>
      {job.application_link && (
        <a href={job.application_link} target="_blank" rel="noopener noreferrer" className="apply-btn">
          Apply Now
        </a>
      )}
    </div>
  </div>
);

const TrendingJobItem = ({ job }) => (
  <div className="trending-job-item">
    <div className="job-info">
      <h4><a href={`/jobs/${job.slug}`}>{job.title}</a></h4>
      <div className="job-meta">
        <span>{job.source_name}</span>
        <span>{job.total_posts} Posts</span>
        {job.days_remaining > 0 && (
          <span>{job.days_remaining} days left</span>
        )}
      </div>
    </div>
    <div className="trending-indicator">
      <span className="fire-icon">🔥</span>
    </div>
  </div>
);

export default HomePage;
