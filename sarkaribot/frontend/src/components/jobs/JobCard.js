import React from 'react';
import { Link } from 'react-router-dom';

const JobCard = ({ job, variant = 'default' }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'TBD';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      announced: { label: 'New', color: 'success' },
      admit_card: { label: 'Admit Card', color: 'warning' },
      answer_key: { label: 'Answer Key', color: 'primary' },
      result: { label: 'Result', color: 'danger' },
    };

    const config = statusConfig[status] || { label: 'Unknown', color: 'secondary' };
    return (
      <span className={`badge badge-${config.color}`}>
        {config.label}
      </span>
    );
  };

  const getDaysRemaining = (endDate) => {
    if (!endDate) return null;
    const today = new Date();
    const end = new Date(endDate);
    const diffTime = end - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'Expired';
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return '1 day left';
    return `${diffDays} days left`;
  };

  const daysRemaining = getDaysRemaining(job.application_end_date);
  const isUrgent = job.days_remaining && job.days_remaining <= 7;

  if (variant === 'compact') {
    return (
      <div className="card hover:shadow-medium transition-all duration-200">
        <div className="card-body p-4">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-semibold text-gray-900 line-clamp-2 flex-1 mr-2">
              <Link 
                to={`/jobs/${job.slug}`} 
                className="hover:text-primary-600 transition-colors duration-200"
              >
                {job.title}
              </Link>
            </h3>
            {job.is_new && getStatusBadge(job.status)}
          </div>
          
          <div className="space-y-1 text-sm text-gray-600">
            <div className="flex items-center">
              <span className="font-medium">{job.source_name}</span>
              <span className="mx-2">•</span>
              <span>{job.total_posts} Posts</span>
            </div>
            
            {job.application_end_date && (
              <div className={`text-sm ${isUrgent ? 'text-danger-600 font-medium' : 'text-gray-600'}`}>
                Last Date: {formatDate(job.application_end_date)}
                {daysRemaining && (
                  <span className="ml-2">({daysRemaining})</span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card hover:shadow-medium transition-all duration-200 border-l-4 border-l-primary-500">
      <div className="card-body">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
              <Link 
                to={`/jobs/${job.slug}`} 
                className="hover:text-primary-600 transition-colors duration-200"
              >
                {job.title}
              </Link>
            </h3>
            
            <div className="flex flex-wrap gap-2 mb-3">
              {getStatusBadge(job.status)}
              {job.is_new && (
                <span className="badge badge-success">New</span>
              )}
              {isUrgent && (
                <span className="badge badge-danger">Urgent</span>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-600">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-6a1 1 0 00-1-1H9a1 1 0 00-1 1v6a1 1 0 01-1 1H4a1 1 0 110-2V4z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">{job.source_name}</span>
            </div>
            
            <div className="flex items-center text-sm text-gray-600">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
              <span>{job.total_posts} Total Posts</span>
            </div>

            <div className="flex items-center text-sm text-gray-600">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
              <span>{job.qualification}</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-600">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
              <span>{job.category_name}</span>
            </div>

            {job.notification_date && (
              <div className="flex items-center text-sm text-gray-600">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                </svg>
                <span>Published: {formatDate(job.notification_date)}</span>
              </div>
            )}

            {job.application_end_date && (
              <div className={`flex items-center text-sm ${isUrgent ? 'text-danger-600 font-medium' : 'text-gray-600'}`}>
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
                <span>
                  Last Date: {formatDate(job.application_end_date)}
                  {daysRemaining && (
                    <span className="ml-2 font-medium">({daysRemaining})</span>
                  )}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
          <Link
            to={`/jobs/${job.slug}`}
            className="btn btn-primary flex-1 sm:flex-none"
          >
            View Details
          </Link>
          
          {job.application_link && (
            <a
              href={job.application_link}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-success flex-1 sm:flex-none"
            >
              Apply Now
            </a>
          )}
          
          <button
            className="btn btn-secondary"
            title="Bookmark this job"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobCard;
