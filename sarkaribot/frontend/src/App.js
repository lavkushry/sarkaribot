import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';

// API Service Layer - Integrates with working backend endpoints
const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api/v1';

const api = {
  getStats: () => fetch(`${API_BASE}/stats/`).then(res => res.json()),
  getJobs: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    return fetch(`${API_BASE}/jobs/?${queryString}`).then(res => res.json());
  },
  getJobsByStatus: (status) => fetch(`${API_BASE}/jobs/?status=${status}`).then(res => res.json()),
  getCategories: () => fetch(`${API_BASE}/categories/`).then(res => res.json()),
  getRecentJobs: () => fetch(`${API_BASE}/jobs/recent/`).then(res => res.json()),
  getTrendingJobs: () => fetch(`${API_BASE}/jobs/trending/`).then(res => res.json()),
  getFeaturedJobs: () => fetch(`${API_BASE}/jobs/featured/`).then(res => res.json()),
  searchJobs: (query) => fetch(`${API_BASE}/search/?q=${encodeURIComponent(query)}`).then(res => res.json()),
  getSources: () => fetch(`${API_BASE}/sources/`).then(res => res.json()),
  getHealth: () => fetch(`${API_BASE}/health/`).then(res => res.json()),
};

// Utility Components
const LoadingSpinner = ({ size = 'medium' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };
  
  return (
    <div className="flex justify-center items-center p-4">
      <div className={`${sizeClasses[size]} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`}></div>
    </div>
  );
};

const ErrorMessage = ({ message, onRetry }) => (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
    <p className="text-red-700 mb-2">{message}</p>
    {onRetry && (
      <button 
        onClick={onRetry}
        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
      >
        Try Again
      </button>
    )}
  </div>
);

// Header Component - SarkariExam.com inspired design
const Header = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="container mx-auto px-4">
        {/* Top Bar */}
        <div className="flex items-center justify-between py-2 text-sm border-b border-gray-200">
          <div className="flex items-center space-x-4 text-gray-600">
            <span>📧 info@sarkaribot.com</span>
            <span>📞 +91 9876543210</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-red-600 font-semibold">🔴 LIVE</span>
            <span className="text-gray-600">Latest Government Jobs</span>
          </div>
        </div>

        {/* Main Header */}
        <div className="flex items-center justify-between py-4">
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">SarkariBot</h1>
              <p className="text-sm text-gray-600">Government Jobs Portal</p>
            </div>
          </Link>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search jobs, exams, results..."
                className="w-full px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                className="absolute right-0 top-0 h-full px-4 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 transition-colors"
              >
                🔍
              </button>
            </div>
          </form>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-gray-600"
          >
            ☰
          </button>
        </div>

        {/* Navigation */}
        <nav className={`${mobileMenuOpen ? 'block' : 'hidden'} md:block pb-4`}>
          <ul className="flex flex-col md:flex-row md:space-x-8 space-y-2 md:space-y-0">
            <li><Link to="/" className="block px-4 py-2 text-blue-600 font-semibold hover:bg-blue-50 rounded">🏠 Home</Link></li>
            <li><Link to="/latest-jobs" className="block px-4 py-2 hover:bg-blue-50 rounded">📋 Latest Jobs</Link></li>
            <li><Link to="/admit-card" className="block px-4 py-2 hover:bg-blue-50 rounded">🎫 Admit Card</Link></li>
            <li><Link to="/answer-key" className="block px-4 py-2 hover:bg-blue-50 rounded">🔑 Answer Key</Link></li>
            <li><Link to="/result" className="block px-4 py-2 hover:bg-blue-50 rounded">🏆 Result</Link></li>
            <li><Link to="/categories" className="block px-4 py-2 hover:bg-blue-50 rounded">📁 Categories</Link></li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

// Footer Component
const Footer = () => (
  <footer className="bg-gray-800 text-white py-8 mt-12">
    <div className="container mx-auto px-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <h3 className="text-lg font-semibold mb-4">SarkariBot</h3>
          <p className="text-gray-300 text-sm">
            Your trusted source for latest government job notifications, admit cards, and results.
          </p>
        </div>
        <div>
          <h4 className="font-semibold mb-4">Quick Links</h4>
          <ul className="space-y-2 text-sm">
            <li><Link to="/latest-jobs" className="text-gray-300 hover:text-white">Latest Jobs</Link></li>
            <li><Link to="/admit-card" className="text-gray-300 hover:text-white">Admit Card</Link></li>
            <li><Link to="/result" className="text-gray-300 hover:text-white">Results</Link></li>
            <li><Link to="/categories" className="text-gray-300 hover:text-white">Categories</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-4">Popular Categories</h4>
          <ul className="space-y-2 text-sm">
            <li><Link to="/category/banking-finance" className="text-gray-300 hover:text-white">Banking Jobs</Link></li>
            <li><Link to="/category/railway-jobs" className="text-gray-300 hover:text-white">Railway Jobs</Link></li>
            <li><Link to="/category/defense-jobs" className="text-gray-300 hover:text-white">Defense Jobs</Link></li>
            <li><Link to="/category/teaching-jobs" className="text-gray-300 hover:text-white">Teaching Jobs</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-4">Contact Info</h4>
          <ul className="space-y-2 text-sm text-gray-300">
            <li>📧 info@sarkaribot.com</li>
            <li>📞 +91 9876543210</li>
            <li>🌐 www.sarkaribot.com</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-gray-700 mt-8 pt-4 text-center text-sm text-gray-400">
        <p>&copy; 2025 SarkariBot. All rights reserved. | Automated Government Job Portal</p>
      </div>
    </div>
  </footer>
);

// Dashboard Stats Component - Integrates with /api/v1/stats/
const DashboardStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await api.getStats();
        setStats(data);
      } catch (err) {
        setError('Failed to load statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!stats) return null;

  const statCards = [
    { title: 'Total Jobs', value: stats.total_jobs, icon: '📋', color: 'bg-blue-500' },
    { title: 'Active Jobs', value: stats.active_jobs, icon: '🔴', color: 'bg-green-500' },
    { title: 'New Today', value: stats.new_jobs_today, icon: '⭐', color: 'bg-yellow-500' },
    { title: 'Categories', value: stats.categories_count, icon: '📁', color: 'bg-purple-500' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      {statCards.map((stat, index) => (
        <div key={index} className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className={`w-12 h-12 ${stat.color} rounded-full flex items-center justify-center mx-auto mb-3`}>
            <span className="text-white text-2xl">{stat.icon}</span>
          </div>
          <h3 className="text-2xl font-bold text-gray-800">{stat.value.toLocaleString()}</h3>
          <p className="text-gray-600 text-sm">{stat.title}</p>
        </div>
      ))}
    </div>
  );
};

// Job Card Component - Displays individual job with SarkariExam.com styling
const JobCard = ({ job }) => {
  const getStatusBadge = (status) => {
    const statusConfig = {
      announced: { label: 'Latest Job', class: 'bg-green-100 text-green-800' },
      admit_card: { label: 'Admit Card', class: 'bg-blue-100 text-blue-800' },
      answer_key: { label: 'Answer Key', class: 'bg-yellow-100 text-yellow-800' },
      result: { label: 'Result', class: 'bg-purple-100 text-purple-800' },
    };
    
    const config = statusConfig[status] || { label: status, class: 'bg-gray-100 text-gray-800' };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${config.class}`}>
        {config.label}
      </span>
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { 
      day: 'numeric', 
      month: 'short', 
      year: 'numeric' 
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-200">
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-start mb-3">
          {getStatusBadge(job.status)}
          {job.is_new && (
            <span className="bg-red-500 text-white px-2 py-1 rounded text-xs font-bold animate-pulse">
              NEW
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2 hover:text-blue-600 cursor-pointer">
          <Link to={`/job/${job.slug}`}>{job.title}</Link>
        </h3>

        {/* Job Details */}
        <div className="space-y-2 text-sm text-gray-600 mb-4">
          <div className="flex items-center">
            <span className="w-4 h-4 mr-2">🏢</span>
            <span>{job.source_name}</span>
          </div>
          <div className="flex items-center">
            <span className="w-4 h-4 mr-2">📁</span>
            <span>{job.category_name}</span>
          </div>
          <div className="flex items-center">
            <span className="w-4 h-4 mr-2">👥</span>
            <span>{job.total_posts.toLocaleString()} Posts</span>
          </div>
          <div className="flex items-center">
            <span className="w-4 h-4 mr-2">🎓</span>
            <span className="line-clamp-1">{job.qualification}</span>
          </div>
        </div>

        {/* Dates */}
        <div className="bg-gray-50 rounded-lg p-3 mb-4">
          <div className="flex justify-between text-sm">
            <div>
              <p className="text-gray-500">Last Date:</p>
              <p className="font-semibold text-red-600">{formatDate(job.application_end_date)}</p>
            </div>
            <div className="text-right">
              <p className="text-gray-500">Days Left:</p>
              <p className={`font-semibold ${job.days_remaining <= 7 ? 'text-red-600' : 'text-green-600'}`}>
                {job.days_remaining} days
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <Link
            to={`/job/${job.slug}`}
            className="flex-1 bg-blue-600 text-white text-center py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm font-semibold"
          >
            View Details
          </Link>
          <a
            href={job.application_link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 bg-green-600 text-white text-center py-2 px-4 rounded-lg hover:bg-green-700 transition-colors text-sm font-semibold"
          >
            Apply Now
          </a>
        </div>
      </div>
    </div>
  );
};

// Jobs List Component - Integrates with multiple API endpoints
const JobsList = ({ 
  title = "Latest Government Jobs", 
  apiEndpoint = '/jobs',
  filters = {},
  showStats = false,
  maxItems = null 
}) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchJobs = async (page = 1) => {
    setLoading(true);
    try {
      let data;
      const params = { ...filters, page, ...(maxItems && { page_size: maxItems }) };
      
      if (apiEndpoint === '/jobs/recent') {
        data = await api.getRecentJobs();
      } else if (apiEndpoint === '/jobs/trending') {
        data = await api.getTrendingJobs();
      } else if (apiEndpoint === '/jobs/featured') {
        data = await api.getFeaturedJobs();
      } else {
        data = await api.getJobs(params);
      }
      
      setJobs(data.results || []);
      setPagination(data);
    } catch (err) {
      setError('Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs(currentPage);
  }, [currentPage, apiEndpoint, JSON.stringify(filters)]);

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={() => fetchJobs(currentPage)} />;

  return (
    <section className="mb-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
        {showStats && pagination && (
          <span className="text-gray-600 text-sm">
            Showing {jobs.length} of {pagination.count} jobs
          </span>
        )}
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No jobs found. Check back later for updates!</p>
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {jobs.map(job => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>

          {/* Pagination */}
          {pagination && pagination.total_pages > 1 && !maxItems && (
            <div className="flex justify-center mt-8">
              <div className="flex space-x-2">
                {pagination.previous && (
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    ← Previous
                  </button>
                )}
                
                <span className="px-4 py-2 bg-gray-100 rounded">
                  Page {pagination.current_page} of {pagination.total_pages}
                </span>
                
                {pagination.next && (
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Next →
                  </button>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
};

// Category Filter Component - Integrates with /api/v1/categories/
const CategoryFilter = ({ selectedCategory, onCategoryChange }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await api.getCategories();
        setCategories(data.results || []);
      } catch (err) {
        console.error('Failed to load categories:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  if (loading) return <LoadingSpinner size="small" />;

  return (
    <div className="mb-6">
      <h3 className="text-lg font-semibold mb-3">Filter by Category</h3>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onCategoryChange(null)}
          className={`px-4 py-2 rounded-lg transition-colors ${
            selectedCategory === null
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
          }`}
        >
          All Categories
        </button>
        {categories.map(category => (
          <button
            key={category.slug}
            onClick={() => onCategoryChange(category.slug)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedCategory === category.slug
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
            }`}
          >
            {category.name} ({category.job_count || 0})
          </button>
        ))}
      </div>
    </div>
  );
};

// Sidebar Components
const TrendingJobs = () => (
  <div className="bg-white rounded-lg shadow-md p-6 mb-6">
    <h3 className="text-lg font-semibold mb-4 text-gray-800">🔥 Trending Jobs</h3>
    <JobsList 
      title=""
      apiEndpoint="/jobs/trending"
      maxItems={3}
      showStats={false}
    />
  </div>
);

const QuickLinks = () => {
  const links = [
    { title: 'SSC CGL 2025', url: '/search?q=SSC+CGL', icon: '📝' },
    { title: 'UPSC CSE 2025', url: '/search?q=UPSC+CSE', icon: '🏛️' },
    { title: 'Bank PO Jobs', url: '/category/banking-finance', icon: '🏦' },
    { title: 'Railway Jobs', url: '/category/railway-jobs', icon: '🚂' },
    { title: 'Teaching Jobs', url: '/category/teaching-jobs', icon: '👩‍🏫' },
    { title: 'Defense Jobs', url: '/category/defense-jobs', icon: '🛡️' },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">⚡ Quick Links</h3>
      <ul className="space-y-2">
        {links.map((link, index) => (
          <li key={index}>
            <Link
              to={link.url}
              className="flex items-center p-2 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded transition-colors"
            >
              <span className="mr-3">{link.icon}</span>
              <span className="text-sm">{link.title}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

// Page Components
const SearchResults = () => {
  const params = new URLSearchParams(window.location.search);
  const query = params.get('q') || '';
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Search Results for "{query}"</h1>
      <JobsList 
        title={`Results for "${query}"`}
        apiEndpoint="/search"
        filters={{ q: query }}
        showStats={true}
      />
    </div>
  );
};

const CategoriesPage = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await api.getCategories();
        setCategories(data.results || []);
      } catch (err) {
        console.error('Failed to load categories:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">📁 Job Categories</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {categories.map(category => (
          <Link
            key={category.slug}
            to={`/category/${category.slug}`}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl font-semibold mb-2">{category.name}</h3>
            <p className="text-gray-600">{category.job_count || 0} jobs available</p>
          </Link>
        ))}
      </div>
    </div>
  );
};

const CategoryPage = () => {
  const { slug } = useParams();
  
  return (
    <JobsList 
      title={`Jobs in ${slug.replace('-', ' ')}`}
      filters={{ category: slug }}
      showStats={true}
    />
  );
};

const JobDetailPage = () => {
  const { slug } = useParams();
  
  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <h1 className="text-3xl font-bold mb-4">Job Details</h1>
      <p className="text-gray-600">Job details for: {slug}</p>
      <p className="mt-4 text-sm text-gray-500">
        This page would show detailed job information fetched from /api/v1/jobs/{slug}/
      </p>
    </div>
  );
};

// Main App Component
export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        
        <main className="container mx-auto px-4 py-8">
          <Routes>
            {/* Home Page */}
            <Route path="/" element={
              <>
                <DashboardStats />
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                  <div className="lg:col-span-3">
                    <CategoryFilter 
                      selectedCategory={null}
                      onCategoryChange={() => {}}
                    />
                    <JobsList 
                      title="🆕 Latest Government Jobs"
                      showStats={true}
                    />
                  </div>
                  <aside className="lg:col-span-1">
                    <TrendingJobs />
                    <QuickLinks />
                  </aside>
                </div>
              </>
            } />
            
            {/* Category Pages - Using working API endpoints */}
            <Route path="/latest-jobs" element={
              <JobsList 
                title="📋 Latest Jobs" 
                filters={{ status: 'announced' }}
                showStats={true}
              />
            } />
            
            <Route path="/admit-card" element={
              <JobsList 
                title="🎫 Admit Card Notifications" 
                filters={{ status: 'admit_card' }}
                showStats={true}
              />
            } />
            
            <Route path="/answer-key" element={
              <JobsList 
                title="🔑 Answer Key Notifications" 
                filters={{ status: 'answer_key' }}
                showStats={true}
              />
            } />
            
            <Route path="/result" element={
              <JobsList 
                title="🏆 Result Notifications" 
                filters={{ status: 'result' }}
                showStats={true}
              />
            } />

            {/* Search Results */}
            <Route path="/search" element={<SearchResults />} />
            
            {/* Categories */}
            <Route path="/categories" element={<CategoriesPage />} />
            <Route path="/category/:slug" element={<CategoryPage />} />
            
            {/* Job Detail */}
            <Route path="/job/:slug" element={<JobDetailPage />} />
          </Routes>
        </main>
        
        <Footer />
      </div>
    </Router>
  );
}
