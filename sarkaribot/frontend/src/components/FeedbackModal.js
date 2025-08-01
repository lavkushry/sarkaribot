/**
 * User Feedback Component for Error Reporting
 */
import React, { useState } from 'react';
import PropTypes from 'prop-types';

const FeedbackModal = ({ isOpen, onClose, errorInfo = null }) => {
  const [feedback, setFeedback] = useState({
    type: 'bug_report',
    message: '',
    contact_info: '',
    page_url: window.location.href
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch('/api/v1/monitoring/feedback/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...feedback,
          user_data: {
            ...errorInfo,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
          },
          browser_info: {
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            viewport: {
              width: window.innerWidth,
              height: window.innerHeight
            }
          }
        })
      });

      if (response.ok) {
        setSubmitted(true);
        setTimeout(() => {
          onClose();
          setSubmitted(false);
          setFeedback({
            type: 'bug_report',
            message: '',
            contact_info: '',
            page_url: window.location.href
          });
        }, 2000);
      } else {
        throw new Error('Failed to submit feedback');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  if (submitted) {
    return (
      <div className="feedback-modal-overlay">
        <div className="feedback-modal">
          <div className="feedback-success">
            <h3>Thank you!</h3>
            <p>Your feedback has been submitted successfully.</p>
            <div className="success-icon">✓</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-modal-overlay" onClick={onClose}>
      <div className="feedback-modal" onClick={(e) => e.stopPropagation()}>
        <div className="feedback-header">
          <h3>Report an Issue</h3>
          <button 
            className="close-button" 
            onClick={onClose}
            type="button"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="feedback-form">
          <div className="form-group">
            <label htmlFor="feedback-type">Issue Type:</label>
            <select
              id="feedback-type"
              value={feedback.type}
              onChange={(e) => setFeedback({ ...feedback, type: e.target.value })}
              required
            >
              <option value="bug_report">Bug Report</option>
              <option value="error_feedback">Error Feedback</option>
              <option value="suggestion">Suggestion</option>
              <option value="complaint">Complaint</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="feedback-message">Description:</label>
            <textarea
              id="feedback-message"
              value={feedback.message}
              onChange={(e) => setFeedback({ ...feedback, message: e.target.value })}
              placeholder="Please describe the issue you encountered..."
              rows="4"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="feedback-contact">Email (optional):</label>
            <input
              id="feedback-contact"
              type="email"
              value={feedback.contact_info}
              onChange={(e) => setFeedback({ ...feedback, contact_info: e.target.value })}
              placeholder="your@email.com"
            />
            <small>We'll use this to follow up on your report</small>
          </div>

          {errorInfo && (
            <div className="error-info">
              <p><strong>Error Details:</strong></p>
              <pre>{JSON.stringify(errorInfo, null, 2)}</pre>
            </div>
          )}

          <div className="form-actions">
            <button 
              type="button" 
              onClick={onClose}
              className="btn btn-secondary"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button 
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

FeedbackModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  errorInfo: PropTypes.object,
};

export default FeedbackModal;