import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/api.ts';
import './JobDetailPage.css';

const JobDetailPage = () => {
  const { slug } = useParams();
  const [loading, setLoading] = useState(true);
  const [job, setJob] = useState(null);
  const [similarJobs, setSimilarJobs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadJobDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const jobData = await apiService.getJobBySlug(slug);
        setJob(jobData);
        
        // Load similar jobs if job ID is available
        if (jobData.id) {
          try {
            const similarData = await apiService.getSimilarJobs(jobData.id);
            setSimilarJobs(similarData.results || similarData);
          } catch (err) {
            console.warn('Failed to load similar jobs:', err);
          }
        }
      } catch (err) {
        console.error('Job detail loading failed:', err);
        setError('Job not found or failed to load. Please try again.');
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
    return (
      <div className="job-detail-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="job-detail-error">
        <div className="error-message">
          <h2>Job Not Found</h2>
          <p>{error || 'The requested job posting could not be found.'}</p>
          <a href="/" className="back-home-btn">← Back to Home</a>
        </div>
      </div>
    );
  }

  return (
    <div className="job-detail-page">
      {/* Breadcrumbs */}
      <nav className="breadcrumbs">
        <div className="container">
          <a href="/">Home</a>
          <span className="separator">›</span>
          <a href="/jobs">Jobs</a>
          <span className="separator">›</span>
          <a href={`/category/${job.category?.slug}`}>{job.category?.name}</a>
          <span className="separator">›</span>
          <span className="current">{job.title}</span>
        </div>
      </nav>

      <div className="container">
        <div className="job-detail-content">
          {/* Main Content */}
          <div className="main-content">
            {/* Job Header */}
            <div className="job-header">
              <div className="job-title-section">
                <h1>{job.title}</h1>
                <div className="job-badges">
                  {job.is_new && <span className="badge new-badge">New</span>}
                  {job.is_expiring_soon && <span className="badge urgent-badge">Urgent</span>}
                  <span className="badge status-badge">{job.category?.name}</span>
                </div>
              </div>
              <div className="job-meta">
                <div className="meta-item">
                  <strong>Organization:</strong> {job.source?.display_name || job.source?.name}
                </div>
                <div className="meta-item">
                  <strong>Total Posts:</strong> {job.total_posts?.toLocaleString()}
                </div>
                <div className="meta-item">
                  <strong>Department:</strong> {job.department || 'Not specified'}
                </div>
                <div className="meta-item">
                  <strong>Posted:</strong> {new Date(job.created_at).toLocaleDateString('en-IN')}
                </div>
              </div>
            </div>

            {/* Important Dates */}
            <div className="important-dates">
              <h2>Important Dates</h2>
              <div className="dates-grid">
                {job.notification_date && (
                  <div className="date-item">
                    <span className="date-label">Notification Date:</span>
                    <span className="date-value">{new Date(job.notification_date).toLocaleDateString('en-IN')}</span>
                  </div>
                )}
                {job.application_end_date && (
                  <div className="date-item">
                    <span className="date-label">Last Date to Apply:</span>
                    <span className="date-value">
                      {new Date(job.application_end_date).toLocaleDateString('en-IN')}
                      {job.days_remaining > 0 && (
                        <span className="days-remaining">({job.days_remaining} days left)</span>
                      )}
                    </span>
                  </div>
                )}
                {job.exam_date && (
                  <div className="date-item">
                    <span className="date-label">Exam Date:</span>
                    <span className="date-value">{new Date(job.exam_date).toLocaleDateString('en-IN')}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Job Description */}
            <div className="job-description">
              <h2>Job Description</h2>
              <div className="description-content">
                {job.description ? (
                  <div dangerouslySetInnerHTML={{ __html: job.description }} />
                ) : (
                  <p>Complete job details will be available in the official notification.</p>
                )}
              </div>
            </div>

            {/* Eligibility Criteria */}
            {job.qualification && (
              <div className="eligibility-section">
                <h2>Eligibility Criteria</h2>
                <div className="eligibility-content">
                  <div className="eligibility-item">
                    <strong>Educational Qualification:</strong>
                    <p>{job.qualification}</p>
                  </div>
                  {(job.min_age || job.max_age) && (
                    <div className="eligibility-item">
                      <strong>Age Limit:</strong>
                      <p>
                        {job.min_age && `Minimum: ${job.min_age} years`}
                        {job.min_age && job.max_age && ' | '}
                        {job.max_age && `Maximum: ${job.max_age} years`}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Application Fee */}
            {job.application_fee && (
              <div className="application-fee">
                <h2>Application Fee</h2>
                <p>{job.application_fee}</p>
              </div>
            )}

            {/* Salary Information */}
            {(job.salary_min || job.salary_max) && (
              <div className="salary-info">
                <h2>Salary Details</h2>
                <p>
                  {job.salary_min && `₹${job.salary_min.toLocaleString()}`}
                  {job.salary_min && job.salary_max && ' - '}
                  {job.salary_max && `₹${job.salary_max.toLocaleString()}`}
                  {(!job.salary_min && !job.salary_max) && 'As per government norms'}
                </p>
              </div>
            )}

            {/* How to Apply */}
            <div className="how-to-apply">
              <h2>How to Apply</h2>
              <div className="apply-content">
                <p>Candidates can apply through the official website or notification link provided below.</p>
                <div className="apply-buttons">
                  {job.application_link && (
                    <a 
                      href={job.application_link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="apply-btn primary"
                    >
                      Apply Online
                    </a>
                  )}
                  {job.notification_pdf && (
                    <a 
                      href={job.notification_pdf} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="apply-btn secondary"
                    >
                      Download Notification
                    </a>
                  )}
                  {job.source_url && (
                    <a 
                      href={job.source_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="apply-btn secondary"
                    >
                      Official Website
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* Milestones */}
            {job.milestones && job.milestones.length > 0 && (
              <div className="milestones-section">
                <h2>Important Updates</h2>
                <div className="milestones-list">
                  {job.milestones.map((milestone) => (
                    <div key={milestone.id} className="milestone-item">
                      <div className="milestone-date">
                        {new Date(milestone.date).toLocaleDateString('en-IN')}
                      </div>
                      <div className="milestone-content">
                        <h3>{milestone.title}</h3>
                        <p>{milestone.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="sidebar">
            {/* Quick Info */}
            <div className="quick-info-card">
              <h3>Quick Information</h3>
              <div className="info-list">
                <div className="info-item">
                  <span className="label">Status:</span>
                  <span className="value">{job.application_status}</span>
                </div>
                <div className="info-item">
                  <span className="label">Posts:</span>
                  <span className="value">{job.total_posts?.toLocaleString()}</span>
                </div>
                <div className="info-item">
                  <span className="label">Category:</span>
                  <span className="value">{job.category?.name}</span>
                </div>
                <div className="info-item">
                  <span className="label">Source:</span>
                  <span className="value">{job.source?.display_name}</span>
                </div>
              </div>
            </div>

            {/* Similar Jobs */}
            {similarJobs.length > 0 && (
              <div className="similar-jobs-card">
                <h3>Similar Jobs</h3>
                <div className="similar-jobs-list">
                  {similarJobs.slice(0, 5).map((similarJob) => (
                    <div key={similarJob.id} className="similar-job-item">
                      <a href={`/jobs/${similarJob.slug}`}>
                        <h4>{similarJob.title}</h4>
                        <p>{similarJob.source_name} • {similarJob.total_posts} Posts</p>
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Share */}
            <div className="share-card">
              <h3>Share this Job</h3>
              <div className="share-buttons">
                <button 
                  onClick={() => navigator.share && navigator.share({
                    title: job.title,
                    url: window.location.href
                  })}
                  className="share-btn"
                >
                  📱 Share
                </button>
                <button 
                  onClick={() => navigator.clipboard.writeText(window.location.href)}
                  className="share-btn"
                >
                  📋 Copy Link
                </button>
              </div>
            </div>
          </div>
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

export default JobDetailPage;
