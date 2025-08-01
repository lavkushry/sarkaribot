/**
 * API service for SarkariBot frontend
 * Handles all HTTP requests to the Django backend
 */

import axios, { AxiosResponse, AxiosError } from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for adding auth tokens
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Types for API responses
export interface JobPosting {
  id: number;
  title: string;
  slug: string;
  description: string;
  department: string;
  qualification: string;
  location: string;
  state: string;
  total_posts: number;
  min_age: number;
  max_age: number;
  application_fee: number;
  salary_min: number;
  salary_max: number;
  notification_date: string;
  application_end_date: string;
  exam_date: string;
  status: 'announced' | 'admit_card' | 'answer_key' | 'result';
  source: {
    id: number;
    name: string;
    website_type: string;
  };
  category: {
    id: number;
    name: string;
    slug: string;
  };
  application_link: string;
  notification_pdf: string;
  keywords: string;
  seo_title: string;
  seo_description: string;
  created_at: string;
  updated_at: string;
  days_remaining: number;
  is_new: boolean;
  is_trending: boolean;
}

export interface JobCategory {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon: string;
  job_count: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface JobStats {
  total_jobs: number;
  total_sources: number;
  jobs_today: number;
  jobs_this_week: number;
  jobs_this_month: number;
  active_jobs: number;
  admit_card_jobs: number;
  answer_key_jobs: number;
  result_jobs: number;
  popular_categories: Array<{
    name: string;
    count: number;
  }>;
}

export interface JobFilters {
  status?: string;
  category?: string;
  source?: string;
  location?: string;
  state?: string;
  qualification?: string;
  posted_today?: boolean;
  posted_this_week?: boolean;
  deadline_soon?: boolean;
  free_application?: boolean;
  high_posts?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

// API Service Class
class ApiService {
  // Job Posting APIs
  async getJobs(filters: JobFilters = {}): Promise<PaginatedResponse<JobPosting>> {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });

    const response = await apiClient.get(`/jobs/?${params.toString()}`);
    return response.data;
  }

  async getJob(slug: string): Promise<JobPosting> {
    const response = await apiClient.get(`/jobs/${slug}/`);
    return response.data;
  }

  async getLatestJobs(limit: number = 20): Promise<JobPosting[]> {
    const response = await apiClient.get(`/jobs/latest/?page_size=${limit}`);
    return response.data.results;
  }

  async getTrendingJobs(limit: number = 10): Promise<JobPosting[]> {
    const response = await apiClient.get(`/jobs/trending/?page_size=${limit}`);
    return response.data.results;
  }

  async getRecentJobs(limit: number = 15): Promise<JobPosting[]> {
    const response = await apiClient.get(`/jobs/recent/?page_size=${limit}`);
    return response.data.results;
  }

  async getFeaturedJobs(limit: number = 8): Promise<JobPosting[]> {
    const response = await apiClient.get(`/jobs/featured/?page_size=${limit}`);
    return response.data.results;
  }

  async getJobsByStatus(status: string, limit: number = 20): Promise<JobPosting[]> {
    const response = await apiClient.get(`/jobs/?status=${status}&page_size=${limit}`);
    return response.data.results;
  }

  async searchJobs(query: string, filters: JobFilters = {}): Promise<PaginatedResponse<JobPosting>> {
    const searchFilters = { ...filters, search: query };
    return this.getJobs(searchFilters);
  }

  // Category APIs
  async getCategories(): Promise<JobCategory[]> {
    const response = await apiClient.get('/categories/');
    return response.data.results;
  }

  async getCategory(slug: string): Promise<JobCategory> {
    const response = await apiClient.get(`/categories/${slug}/`);
    return response.data;
  }

  async getCategoryJobs(categorySlug: string, filters: JobFilters = {}): Promise<PaginatedResponse<JobPosting>> {
    const params = new URLSearchParams();
    params.append('category', categorySlug);
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });

    const response = await apiClient.get(`/jobs/?${params.toString()}`);
    return response.data;
  }

  // Stats and Analytics APIs
  async getStats(): Promise<JobStats> {
    const response = await apiClient.get('/stats/');
    return response.data;
  }

  // Contact and Newsletter APIs
  async submitContact(data: {
    name: string;
    email: string;
    subject: string;
    message: string;
  }): Promise<void> {
    await apiClient.post('/contact/', data);
  }

  async subscribeNewsletter(email: string): Promise<void> {
    await apiClient.post('/newsletter/', { email });
  }

  async createJobAlert(data: {
    email: string;
    keywords: string;
    location?: string;
    category?: string;
  }): Promise<void> {
    await apiClient.post('/job-alerts/', data);
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; metrics: any }> {
    const response = await apiClient.get('/health/');
    return response.data;
  }

  // Feed and Sitemap
  async getSitemap(): Promise<any> {
    const response = await apiClient.get('/sitemap/');
    return response.data;
  }

  async getJobFeed(): Promise<any> {
    const response = await apiClient.get('/feed/');
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export utility functions
export const formatDate = (dateString: string): string => {
  if (!dateString) return 'Not specified';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export const formatSalary = (min?: number, max?: number): string => {
  if (!min && !max) return 'Not specified';
  if (min && max) return `₹${min.toLocaleString()} - ₹${max.toLocaleString()}`;
  if (min) return `₹${min.toLocaleString()}+`;
  return `Up to ₹${max?.toLocaleString()}`;
};

export const getJobStatusLabel = (status: string): string => {
  const statusMap: Record<string, string> = {
    'announced': 'Latest Job',
    'admit_card': 'Admit Card',
    'answer_key': 'Answer Key',
    'result': 'Result',
    'archived': 'Archived'
  };
  return statusMap[status] || status;
};

export const getJobStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    'announced': '#28a745',
    'admit_card': '#007bff',
    'answer_key': '#ffc107',
    'result': '#17a2b8',
    'archived': '#6c757d'
  };
  return colorMap[status] || '#6c757d';
};

export default apiService;
