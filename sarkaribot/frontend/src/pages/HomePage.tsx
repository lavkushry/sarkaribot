/**
 * HomePage component for SarkariBot
 * Replicates SarkariExam.com homepage layout with job categories
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { JobPosting, JobCategory, JobStats, apiService, getJobStatusLabel } from '../services/api.ts';
import JobCard from '../components/JobCard.tsx';

const PageContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 30px;
  
  @media (max-width: 968px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const MainContent = styled.main`
  min-height: 600px;
`;

const Sidebar = styled.aside`
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  height: fit-content;
  position: sticky;
  top: 20px;
`;

const CategorySection = styled.section`
  margin-bottom: 40px;
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 3px solid #1e3c72;
`;

const SectionTitle = styled.h2`
  font-size: 22px;
  color: #1e3c72;
  margin: 0;
  font-weight: 600;
`;

const ViewAllLink = styled(Link)`
  color: #1e3c72;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  
  &:hover {
    text-decoration: underline;
  }
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

const StatsCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const StatsTitle = styled.h3`
  font-size: 16px;
  color: #1e3c72;
  margin: 0 0 15px 0;
  font-weight: 600;
`;

const StatsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const StatItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
`;

const StatLabel = styled.span`
  color: #666;
`;

const StatValue = styled.span`
  font-weight: 600;
  color: #1e3c72;
`;

const CategoriesCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const CategoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const CategoryItem = styled(Link)`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  text-decoration: none;
  color: #333;
  font-size: 14px;
  transition: background-color 0.3s;
  
  &:hover {
    background: #f0f0f0;
    color: #1e3c72;
  }
`;

const CategoryCount = styled.span`
  background: #e9ecef;
  color: #495057;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #666;
  
  h3 {
    margin-bottom: 10px;
    color: #333;
  }
  
  p {
    margin: 0;
    line-height: 1.5;
  }
`;

const TabNavigation = styled.div`
  display: flex;
  gap: 0;
  margin-bottom: 30px;
  border-bottom: 1px solid #e0e0e0;
`;

const TabButton = styled.button<{ active: boolean }>`
  background: ${props => props.active ? '#1e3c72' : 'transparent'};
  color: ${props => props.active ? 'white' : '#666'};
  border: none;
  padding: 12px 24px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
  
  &:hover {
    background: ${props => props.active ? '#1e3c72' : '#f8f9fa'};
    color: ${props => props.active ? 'white' : '#1e3c72'};
  }
`;

const HomePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'announced' | 'admit_card' | 'answer_key' | 'result'>('announced');
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [categories, setCategories] = useState<JobCategory[]>([]);
  const [stats, setStats] = useState<JobStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const tabs = [
    { key: 'announced' as const, label: 'Latest Jobs', icon: '🆕' },
    { key: 'admit_card' as const, label: 'Admit Card', icon: '🎫' },
    { key: 'answer_key' as const, label: 'Answer Key', icon: '🔑' },
    { key: 'result' as const, label: 'Result', icon: '📊' },
  ];

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadJobsByStatus(activeTab);
  }, [activeTab]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [categoriesData, statsData] = await Promise.all([
        apiService.getCategories(),
        apiService.getStats(),
      ]);
      
      setCategories(categoriesData.slice(0, 10)); // Show top 10 categories
      setStats(statsData);
    } catch (err) {
      setError('Failed to load data. Please try again later.');
      console.error('Error loading homepage data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadJobsByStatus = async (status: string) => {
    try {
      const jobsData = await apiService.getJobsByStatus(status, 20);
      setJobs(jobsData);
    } catch (err) {
      console.error(`Error loading ${status} jobs:`, err);
      setJobs([]);
    }
  };

  if (loading) {
    return (
      <PageContainer>
        <MainContent>
          <LoadingSpinner>🔄 Loading latest government jobs...</LoadingSpinner>
        </MainContent>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <MainContent>
        {error && <ErrorMessage>{error}</ErrorMessage>}

        {/* Tab Navigation */}
        <TabNavigation>
          {tabs.map((tab) => (
            <TabButton
              key={tab.key}
              active={activeTab === tab.key}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.icon} {tab.label}
            </TabButton>
          ))}
        </TabNavigation>

        {/* Active Tab Content */}
        <CategorySection>
          <SectionHeader>
            <SectionTitle>
              {tabs.find(tab => tab.key === activeTab)?.label || 'Jobs'}
            </SectionTitle>
            <ViewAllLink to={`/jobs/${activeTab}`}>
              View All →
            </ViewAllLink>
          </SectionHeader>

          <JobsList>
            {jobs.length > 0 ? (
              jobs.map((job) => (
                <JobCard 
                  key={job.id} 
                  job={job} 
                  showDescription={false}
                />
              ))
            ) : (
              <EmptyState>
                <h3>No jobs available</h3>
                <p>
                  No {getJobStatusLabel(activeTab).toLowerCase()} available at the moment. 
                  Please check back later or browse other categories.
                </p>
              </EmptyState>
            )}
          </JobsList>
        </CategorySection>
      </MainContent>

      <Sidebar>
        {/* Statistics Card */}
        {stats && (
          <StatsCard>
            <StatsTitle>📊 Job Statistics</StatsTitle>
            <StatsList>
              <StatItem>
                <StatLabel>Total Jobs</StatLabel>
                <StatValue>{stats.total_jobs.toLocaleString()}</StatValue>
              </StatItem>
              <StatItem>
                <StatLabel>Active Jobs</StatLabel>
                <StatValue>{stats.active_jobs.toLocaleString()}</StatValue>
              </StatItem>
              <StatItem>
                <StatLabel>Today's Jobs</StatLabel>
                <StatValue>{stats.jobs_today.toLocaleString()}</StatValue>
              </StatItem>
              <StatItem>
                <StatLabel>This Week</StatLabel>
                <StatValue>{stats.jobs_this_week.toLocaleString()}</StatValue>
              </StatItem>
              <StatItem>
                <StatLabel>Sources</StatLabel>
                <StatValue>{stats.total_sources.toLocaleString()}</StatValue>
              </StatItem>
            </StatsList>
          </StatsCard>
        )}

        {/* Categories Card */}
        <CategoriesCard>
          <StatsTitle>📂 Popular Categories</StatsTitle>
          <CategoryList>
            {categories.map((category) => (
              <CategoryItem key={category.id} to={`/category/${category.slug}`}>
                <span>{category.name}</span>
                <CategoryCount>{category.job_count}</CategoryCount>
              </CategoryItem>
            ))}
            <CategoryItem to="/categories">
              <span style={{ fontWeight: 'bold', color: '#1e3c72' }}>
                View All Categories →
              </span>
            </CategoryItem>
          </CategoryList>
        </CategoriesCard>

        {/* Quick Links */}
        <CategoriesCard>
          <StatsTitle>🔗 Quick Links</StatsTitle>
          <CategoryList>
            <CategoryItem to="/jobs/deadline-soon">
              ⏰ Deadline Soon
            </CategoryItem>
            <CategoryItem to="/jobs/high-posts">
              📈 High Posts Jobs
            </CategoryItem>
            <CategoryItem to="/jobs/free-application">
              💰 Free Application
            </CategoryItem>
            <CategoryItem to="/job-alerts">
              🔔 Job Alerts
            </CategoryItem>
            <CategoryItem to="/syllabus">
              📚 Syllabus
            </CategoryItem>
            <CategoryItem to="/previous-papers">
              📄 Previous Papers
            </CategoryItem>
          </CategoryList>
        </CategoriesCard>
      </Sidebar>
    </PageContainer>
  );
};

export default HomePage;
