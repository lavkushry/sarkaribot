/**
 * JobCard component for displaying job listings
 * Replicates SarkariExam.com job card design
 */

import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { JobPosting, formatDate, formatSalary, getJobStatusLabel, getJobStatusColor } from '../services/api.ts';

const Card = styled.div`
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-color: #1e3c72;
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: flex-start;
  margin-bottom: 15px;
  gap: 15px;
`;

const JobTitle = styled(Link)`
  color: #1e3c72;
  text-decoration: none;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.3;
  flex: 1;
  
  &:hover {
    color: #2a5298;
    text-decoration: underline;
  }
`;

const StatusBadge = styled.span<{ status: string }>`
  background: ${props => getJobStatusColor(props.status)};
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
`;

const Department = styled.div`
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
  font-weight: 500;
`;

const JobDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
`;

const DetailItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #555;
`;

const DetailLabel = styled.span`
  font-weight: 500;
  color: #333;
`;

const DetailValue = styled.span`
  color: #666;
`;

const CardFooter = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
  flex-wrap: wrap;
  gap: 10px;
`;

const SourceInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
`;

const SourceLogo = styled.div`
  width: 24px;
  height: 24px;
  background: #f0f0f0;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  color: #666;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 10px;
`;

const ActionButton = styled.a`
  padding: 8px 16px;
  border-radius: 20px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s;
  
  &.primary {
    background: #1e3c72;
    color: white;
    
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

const NewBadge = styled.span`
  background: #ff6b35;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: bold;
  margin-left: 8px;
`;

const TrendingBadge = styled.span`
  background: #28a745;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: bold;
  margin-left: 8px;
`;

const DeadlineWarning = styled.div<{ urgent?: boolean }>`
  background: ${props => props.urgent ? '#ff6b35' : '#ffc107'};
  color: ${props => props.urgent ? 'white' : '#000'};
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  margin-top: 10px;
  text-align: center;
`;

interface JobCardProps {
  job: JobPosting;
  showDescription?: boolean;
  compact?: boolean;
}

const JobCard: React.FC<JobCardProps> = ({ 
  job, 
  showDescription = false, 
  compact = false 
}) => {
  const getDaysRemaining = () => {
    if (!job.application_end_date) return null;
    
    const endDate = new Date(job.application_end_date);
    const today = new Date();
    const diffTime = endDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
  };

  const daysRemaining = getDaysRemaining();
  const isUrgent = daysRemaining !== null && daysRemaining <= 3 && daysRemaining >= 0;
  const isExpired = daysRemaining !== null && daysRemaining < 0;

  return (
    <Card>
      <CardHeader>
        <JobTitle to={`/jobs/${job.slug}`}>
          {job.title}
          {job.is_new && <NewBadge>NEW</NewBadge>}
          {job.is_trending && <TrendingBadge>HOT</TrendingBadge>}
        </JobTitle>
        <StatusBadge status={job.status}>
          {getJobStatusLabel(job.status)}
        </StatusBadge>
      </CardHeader>

      <Department>{job.department}</Department>

      {showDescription && job.description && (
        <div style={{ 
          color: '#666', 
          fontSize: '14px', 
          lineHeight: '1.5', 
          marginBottom: '15px',
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden'
        }}>
          {job.description}
        </div>
      )}

      <JobDetails>
        {job.total_posts && (
          <DetailItem>
            <DetailLabel>Posts:</DetailLabel>
            <DetailValue>{job.total_posts.toLocaleString()}</DetailValue>
          </DetailItem>
        )}
        
        {job.qualification && (
          <DetailItem>
            <DetailLabel>Qualification:</DetailLabel>
            <DetailValue>{job.qualification}</DetailValue>
          </DetailItem>
        )}
        
        {(job.min_age || job.max_age) && (
          <DetailItem>
            <DetailLabel>Age:</DetailLabel>
            <DetailValue>
              {job.min_age && job.max_age 
                ? `${job.min_age} - ${job.max_age} years`
                : job.min_age 
                ? `${job.min_age}+ years`
                : `Up to ${job.max_age} years`
              }
            </DetailValue>
          </DetailItem>
        )}
        
        {job.location && (
          <DetailItem>
            <DetailLabel>Location:</DetailLabel>
            <DetailValue>{job.location}</DetailValue>
          </DetailItem>
        )}
        
        {(job.salary_min || job.salary_max) && (
          <DetailItem>
            <DetailLabel>Salary:</DetailLabel>
            <DetailValue>{formatSalary(job.salary_min, job.salary_max)}</DetailValue>
          </DetailItem>
        )}
        
        {job.application_fee !== undefined && job.application_fee !== null && (
          <DetailItem>
            <DetailLabel>Fee:</DetailLabel>
            <DetailValue>
              {job.application_fee === 0 ? 'Free' : `₹${job.application_fee}`}
            </DetailValue>
          </DetailItem>
        )}
      </JobDetails>

      {/* Deadline warning */}
      {!isExpired && daysRemaining !== null && daysRemaining <= 7 && (
        <DeadlineWarning urgent={isUrgent}>
          {daysRemaining === 0 
            ? '⚠️ Last day to apply!'
            : daysRemaining === 1
            ? '⚠️ Only 1 day left to apply!'
            : `⏰ ${daysRemaining} days left to apply`
          }
        </DeadlineWarning>
      )}

      {isExpired && (
        <DeadlineWarning urgent>
          ❌ Application deadline expired
        </DeadlineWarning>
      )}

      <CardFooter>
        <SourceInfo>
          <SourceLogo>
            {job.source.name.charAt(0).toUpperCase()}
          </SourceLogo>
          <span>{job.source.name}</span>
          <span>•</span>
          <span>{formatDate(job.created_at)}</span>
          {job.application_end_date && (
            <>
              <span>•</span>
              <span>Last Date: {formatDate(job.application_end_date)}</span>
            </>
          )}
        </SourceInfo>

        <ActionButtons>
          {job.notification_pdf && (
            <ActionButton 
              href={job.notification_pdf} 
              target="_blank" 
              rel="noopener noreferrer"
              className="secondary"
            >
              📄 Notification
            </ActionButton>
          )}
          
          {job.application_link && !isExpired && (
            <ActionButton 
              href={job.application_link} 
              target="_blank" 
              rel="noopener noreferrer"
              className="primary"
            >
              📝 Apply Now
            </ActionButton>
          )}
          
          <ActionButton 
            href={`/jobs/${job.slug}`}
            className="secondary"
          >
            📖 View Details
          </ActionButton>
        </ActionButtons>
      </CardFooter>
    </Card>
  );
};

export default JobCard;
