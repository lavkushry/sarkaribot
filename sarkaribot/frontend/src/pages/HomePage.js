import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiService from '../services/apiService';
import JobCard from '../components/jobs/JobCard';
import LoadingSpinner from '../components/common/LoadingSpinner';

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
        
        const [latestJobs, categories, stats] = await Promise.all([
          apiService.getLatestJobs(),
          apiService.getCategories(),
          apiService.getStats(),
        ]);

        setData({
          latestJobs: latestJobs.results || latestJobs,
          categories: categories.results || categories,
          stats: stats,
          trendingJobs: latestJobs.results?.slice(0, 5) || []
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
    return <LoadingSpinner text="Loading SarkariBot..." />;
  }

  if (error) {
    return (
      <div className="min-h-96 flex items-center justify-center px-4">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Oops! Something went wrong</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="btn btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-purple-800 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 animate-fade-in">
              SarkariBot
              <span className="block text-2xl md:text-3xl font-normal mt-2 text-blue-100">
                Government Jobs Portal
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto animate-slide-up">
              Find the latest government job notifications, admit cards, answer keys, and results - all in one place
            </p>
            
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto mt-12">
              <StatsCard 
                number={data.stats.total_jobs || 0} 
                label="Total Jobs" 
                icon="📋" 
              />
              <StatsCard 
                number={data.stats.active_jobs || 0} 
                label="Active Jobs" 
                icon="🔥" 
              />
              <StatsCard 
                number={data.stats.new_jobs_this_week || 0} 
                label="New This Week" 
                icon="⭐" 
              />
              <StatsCard 
                number={data.stats.sources_active || 0} 
                label="Sources" 
                icon="🏛️" 
              />
            </div>
          </div>
        </div>
      </section>

      {/* Quick Links Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <QuickLinkCard 
              title="Latest Jobs" 
              count={data.stats.jobs_by_status?.announced?.count || 0}
              href="/jobs?status=announced"
              color="bg-green-500"
              icon="🆕"
            />
            <QuickLinkCard 
              title="Admit Card" 
              count={data.stats.jobs_by_status?.admit_card?.count || 0}
              href="/jobs?status=admit_card"
              color="bg-yellow-500"
              icon="🎫"
            />
            <QuickLinkCard 
              title="Answer Key" 
              count={data.stats.jobs_by_status?.answer_key?.count || 0}
              href="/jobs?status=answer_key"
              color="bg-blue-500"
              icon="🔑"
            />
            <QuickLinkCard 
              title="Result" 
              count={data.stats.jobs_by_status?.result?.count || 0}
              href="/jobs?status=result"
              color="bg-red-500"
              icon="📊"
            />
          </div>
        </div>
      </section>

      {/* Latest Jobs Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Latest Government Jobs
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Stay updated with the newest government job opportunities across India
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {data.latestJobs.slice(0, 6).map((job) => (
              <JobCard key={job.id} job={job} variant="compact" />
            ))}
          </div>

          <div className="text-center">
            <Link to="/jobs" className="btn btn-primary btn-lg">
              View All Jobs →
            </Link>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Job Categories
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Explore jobs by category and find opportunities that match your qualifications
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {data.categories.slice(0, 8).map((category) => (
              <CategoryCard 
                key={category.id} 
                category={category}
                jobCount={data.stats.jobs_by_category?.[category.slug]?.count || 0}
              />
            ))}
          </div>

          <div className="text-center mt-12">
            <Link to="/categories" className="btn btn-secondary btn-lg">
              View All Categories →
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Never Miss a Government Job
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Get instant notifications for new job postings, admit cards, and results
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="btn bg-white text-primary-600 hover:bg-gray-100 btn-lg">
              📧 Subscribe to Alerts
            </button>
            <Link to="/jobs" className="btn btn-secondary btn-lg border-white text-white hover:bg-white hover:text-primary-600">
              🔍 Browse Jobs
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

// Supporting Components
const StatsCard = ({ number, label, icon }) => (
  <div className="text-center animate-scale-in">
    <div className="text-3xl mb-2">{icon}</div>
    <div className="text-3xl md:text-4xl font-bold text-yellow-300 mb-1">
      {number.toLocaleString()}
    </div>
    <div className="text-sm md:text-base text-blue-100">
      {label}
    </div>
  </div>
);

const QuickLinkCard = ({ title, count, href, color, icon }) => (
  <Link
    to={href}
    className="card hover:shadow-medium transition-all duration-200 group"
  >
    <div className="card-body text-center">
      <div className={`w-12 h-12 ${color} rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform duration-200`}>
        <span className="text-white text-xl">{icon}</span>
      </div>
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <div className="text-2xl font-bold text-primary-600">{count}</div>
    </div>
  </Link>
);

const CategoryCard = ({ category, jobCount }) => (
  <Link
    to={`/category/${category.slug}`}
    className="card hover:shadow-medium transition-all duration-200 group"
  >
    <div className="card-body text-center">
      <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors duration-200">
        {category.name}
      </h3>
      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
        {category.description}
      </p>
      <div className="text-primary-600 font-medium">
        {jobCount} {jobCount === 1 ? 'Job' : 'Jobs'}
      </div>
    </div>
  </Link>
);

export default HomePage;
