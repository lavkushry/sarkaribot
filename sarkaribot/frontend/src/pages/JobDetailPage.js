import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import apiService from '../services/apiService';
import LoadingSpinner from '../components/common/LoadingSpinner';

const JobDetailPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [relatedJobs, setRelatedJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadJobDetails = async () => {
      try {
        setLoading(true);
        setError(null);

        const [jobData, relatedData] = await Promise.all([
          apiService.getJobBySlug(slug),
          apiService.getLatestJobs({ limit: 5 })
        ]);

        setJob(jobData);
        setRelatedJobs((relatedData.results || relatedData).filter(j => j.slug !== slug));
      } catch (err) {
        console.error('Failed to load job details:', err);
        if (err.response?.status === 404) {
          setError('Job not found. It may have been removed or the URL is incorrect.');
        } else {
          setError('Failed to load job details. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    if (slug) {
      loadJobDetails();
    }
  }, [slug]);

  // SEO metadata update
  useEffect(() => {
    if (job && job.seo_metadata) {
      document.title = job.seo_metadata.title || job.title;
      
      const metaDescription = document.querySelector('meta[name="description"]');
      if (metaDescription) {
        metaDescription.content = job.seo_metadata.description || job.description;
      }
    }
  }, [job]);

  if (loading) {
    return <LoadingSpinner text="Loading job details..." />;
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Job Not Found</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => navigate(-1)}
              className="btn btn-secondary"
            >
              ← Go Back
            </button>
            <Link to="/jobs" className="btn btn-primary">
              Browse All Jobs
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!job) {
    return null;
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      announced: { label: 'Latest Job', class: 'badge-success' },
      admit_card: { label: 'Admit Card', class: 'badge-warning' },
      answer_key: { label: 'Answer Key', class: 'badge-info' },
      result: { label: 'Result', class: 'badge-danger' },
      archived: { label: 'Archived', class: 'badge-secondary' }
    };
    
    const config = statusConfig[status] || statusConfig.announced;
    return <span className={`badge ${config.class}`}>{config.label}</span>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'TBD';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getDaysRemaining = (dateString) => {
    if (!dateString) return null;
    const diff = new Date(dateString) - new Date();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return days > 0 ? days : 0;
  };

  const daysLeft = getDaysRemaining(job.application_end_date);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="mb-6">
        <ol className="flex items-center space-x-2 text-sm text-gray-500">
          <li><Link to="/" className="hover:text-primary-600">Home</Link></li>
          <li>→</li>
          <li><Link to="/jobs" className="hover:text-primary-600">Jobs</Link></li>
          <li>→</li>
          <li><Link to={`/category/${job.category?.slug}`} className="hover:text-primary-600">{job.category?.name}</Link></li>
          <li>→</li>
          <li className="text-gray-900 font-medium">{job.title}</li>
        </ol>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Header */}
          <div className="card mb-6">
            <div className="card-body">
              <div className="flex flex-wrap items-start justify-between mb-4">
                <div className="flex-1 min-w-0">
                  <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
                    {job.title}
                  </h1>
                  <div className="flex flex-wrap items-center gap-3 mb-3">
                    {getStatusBadge(job.status)}
                    {job.is_new && <span className="badge badge-success">New</span>}
                    {job.is_expiring_soon && <span className="badge badge-warning">Urgent</span>}
                    <span className="text-gray-600">by {job.source?.display_name || job.source?.name}</span>
                    <span className="text-gray-600">•</span>
                    <span className="text-gray-600">
                      Posted {formatDate(job.created_at)}
                    </span>
                  </div>
                </div>
                
                {job.application_link && (
                  <div className="flex flex-col sm:flex-row gap-2 mt-4 sm:mt-0">
                    <a
                      href={job.application_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary btn-lg"
                    >
                      Apply Now →
                    </a>
                  </div>
                )}
              </div>

              {daysLeft > 0 && (
                <div className="alert alert-warning">
                  <strong>⏰ Last date to apply: {formatDate(job.application_end_date)}</strong>
                  <span className="ml-2">({daysLeft} days remaining)</span>
                </div>
              )}
            </div>
          </div>

          {/* Job Details */}
          <div className="card mb-6">
            <div className="card-header">
              <h2 className="text-xl font-semibold">Job Details</h2>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <DetailItem label="Organization" value={job.source?.display_name || job.source?.name} />
                <DetailItem label="Category" value={job.category?.name} />
                <DetailItem label="Total Posts" value={job.total_posts?.toLocaleString() || 'Not specified'} />
                <DetailItem label="Department" value={job.department || 'Not specified'} />
                <DetailItem label="Job Location" value={job.job_location || 'Various'} />
                <DetailItem label="Application Mode" value={job.application_mode || 'Online'} />
                <DetailItem label="Application Start" value={formatDate(job.application_start_date)} />
                <DetailItem label="Application End" value={formatDate(job.application_end_date)} />
              </div>
            </div>
          </div>

          {/* Description */}
          {job.description && (
            <div className="card mb-6">
              <div className="card-header">
                <h2 className="text-xl font-semibold">Job Description</h2>
              </div>
              <div className="card-body">
                <div 
                  className="prose max-w-none"
                  dangerouslySetInnerHTML={{ __html: job.description }}
                />
              </div>
            </div>
          )}

          {/* Eligibility */}
          {job.qualification && (
            <div className="card mb-6">
              <div className="card-header">
                <h2 className="text-xl font-semibold">Eligibility Criteria</h2>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Educational Qualification</h4>
                    <p className="text-gray-700">{job.qualification}</p>
                  </div>
                  {(job.min_age || job.max_age) && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Age Limit</h4>
                      <p className="text-gray-700">
                        {job.min_age && `Minimum: ${job.min_age} years`}
                        {job.min_age && job.max_age && ' | '}
                        {job.max_age && `Maximum: ${job.max_age} years`}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Important Dates */}
          <div className="card mb-6">
            <div className="card-header">
              <h2 className="text-xl font-semibold">Important Dates</h2>
            </div>
            <div className="card-body">
              <div className="space-y-3">
                {job.notification_date && (
                  <DateItem 
                    label="Notification Date" 
                    date={job.notification_date}
                    icon="📋"
                  />
                )}
                <DateItem 
                  label="Application Start Date" 
                  date={job.application_start_date}
                  icon="🗓️"
                />
                <DateItem 
                  label="Application End Date" 
                  date={job.application_end_date}
                  icon="⏰"
                  highlight={daysLeft > 0 && daysLeft <= 7}
                />
                {job.exam_date && (
                  <DateItem 
                    label="Exam Date" 
                    date={job.exam_date}
                    icon="📝"
                  />
                )}
              </div>
            </div>
          </div>

          {/* Salary */}
          {(job.salary_min || job.salary_max || job.application_fee) && (
            <div className="card mb-6">
              <div className="card-header">
                <h2 className="text-xl font-semibold">Salary & Fees</h2>
              </div>
              <div className="card-body space-y-4">
                {(job.salary_min || job.salary_max) && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Salary Details</h4>
                    <p className="text-gray-700">
                      {job.salary_min && `₹${job.salary_min.toLocaleString()}`}
                      {job.salary_min && job.salary_max && ' - '}
                      {job.salary_max && `₹${job.salary_max.toLocaleString()}`}
                      {(!job.salary_min && !job.salary_max) && 'As per government norms'}
                    </p>
                  </div>
                )}
                {job.application_fee && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Application Fee</h4>
                    <p className="text-gray-700">{job.application_fee}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Links */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold">Important Links</h2>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {job.notification_pdf && (
                  <LinkButton 
                    href={job.notification_pdf}
                    icon="📋"
                    text="Official Notification"
                  />
                )}
                {job.application_link && (
                  <LinkButton 
                    href={job.application_link}
                    icon="✍️"
                    text="Apply Online"
                    primary
                  />
                )}
                {job.source_url && (
                  <LinkButton 
                    href={job.source_url}
                    icon="🏛️"
                    text="Official Website"
                  />
                )}
                {job.syllabus_link && (
                  <LinkButton 
                    href={job.syllabus_link}
                    icon="📚"
                    text="Syllabus"
                  />
                )}
              </div>
            </div>
          </div>

          {/* Milestones */}
          {job.milestones && job.milestones.length > 0 && (
            <div className="card mt-6">
              <div className="card-header">
                <h2 className="text-xl font-semibold">Important Updates</h2>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  {job.milestones.map((milestone) => (
                    <div key={milestone.id} className="flex gap-4 p-4 bg-gray-50 rounded-lg">
                      <div className="flex-shrink-0 w-16 text-center">
                        <div className="text-sm font-medium text-primary-600">
                          {new Date(milestone.date).toLocaleDateString('en-IN', { 
                            month: 'short', 
                            day: 'numeric' 
                          })}
                        </div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 mb-1">{milestone.title}</h3>
                        <p className="text-gray-600 text-sm">{milestone.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          {/* Quick Info */}
          <div className="card mb-6">
            <div className="card-header">
              <h3 className="text-lg font-semibold">Quick Information</h3>
            </div>
            <div className="card-body space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="font-medium">{job.application_status}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Posts:</span>
                <span className="font-medium">{job.total_posts?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Category:</span>
                <span className="font-medium">{job.category?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Source:</span>
                <span className="font-medium">{job.source?.display_name}</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card mb-6">
            <div className="card-header">
              <h3 className="text-lg font-semibold">Quick Actions</h3>
            </div>
            <div className="card-body space-y-3">
              <button className="btn btn-outline-primary w-full">
                🔖 Bookmark Job
              </button>
              <button className="btn btn-outline-primary w-full">
                📧 Set Alert
              </button>
              <button 
                onClick={() => navigator.share && navigator.share({
                  title: job.title,
                  url: window.location.href
                })}
                className="btn btn-outline-primary w-full"
              >
                📤 Share Job
              </button>
              <button 
                onClick={() => navigator.clipboard.writeText(window.location.href)}
                className="btn btn-outline-primary w-full"
              >
                📋 Copy Link
              </button>
            </div>
          </div>

          {/* Related Jobs */}
          {relatedJobs.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold">Related Jobs</h3>
              </div>
              <div className="card-body space-y-4">
                {relatedJobs.slice(0, 4).map((relatedJob) => (
                  <RelatedJobItem key={relatedJob.id} job={relatedJob} />
                ))}
                <Link 
                  to={`/jobs?category=${job.category?.slug}`}
                  className="btn btn-secondary w-full"
                >
                  View More in {job.category?.name}
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* JSON-LD Structured Data */}
      {job.seo_metadata?.structured_data && (
        <script type="application/ld+json">
          {JSON.stringify(job.seo_metadata.structured_data)}
        </script>
      )}
    </div>
  );
};

// Supporting Components
const DetailItem = ({ label, value }) => (
  <div>
    <dt className="text-sm font-medium text-gray-500">{label}</dt>
    <dd className="mt-1 text-sm text-gray-900">{value}</dd>
  </div>
);

const DateItem = ({ label, date, icon, highlight = false }) => (
  <div className={`flex items-center justify-between p-3 rounded-lg ${highlight ? 'bg-warning-50 border border-warning-200' : 'bg-gray-50'}`}>
    <div className="flex items-center">
      <span className="text-lg mr-3">{icon}</span>
      <span className="font-medium text-gray-900">{label}</span>
    </div>
    <span className={`text-sm ${highlight ? 'text-warning-800 font-semibold' : 'text-gray-600'}`}>
      {date ? new Date(date).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }) : 'TBD'}
    </span>
  </div>
);

const LinkButton = ({ href, icon, text, primary = false }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className={`btn w-full ${primary ? 'btn-primary' : 'btn-outline-primary'}`}
  >
    <span className="mr-2">{icon}</span>
    {text}
  </a>
);

const RelatedJobItem = ({ job }) => (
  <div className="border-l-4 border-primary-200 pl-4">
    <h4 className="font-medium text-gray-900 mb-1">
      <Link 
        to={`/jobs/${job.slug}`}
        className="hover:text-primary-600 transition-colors duration-200"
      >
        {job.title}
      </Link>
    </h4>
    <div className="text-sm text-gray-600">
      <span>{job.source_name}</span>
      {job.total_posts && (
        <>
          <span className="mx-1">•</span>
          <span>{job.total_posts} Posts</span>
        </>
      )}
    </div>
  </div>
);

export default JobDetailPage;
