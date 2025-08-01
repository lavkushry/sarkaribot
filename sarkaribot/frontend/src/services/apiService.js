/**
 * API Service for SarkariBot Frontend
 * Handles all API communication with proper error handling
 */

import axios from 'axios';

class ApiService {
  constructor() {
    this.baseURL = 'http://localhost:8000';
    
    // Create axios instance
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });
    
    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(this.handleError(error));
      }
    );
  }
  
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data?.message || 'Server error',
        status: error.response.status,
        data: error.response.data
      };
    } else if (error.request) {
      // Network error
      return {
        message: 'Network error - please check your connection',
        status: 0,
        data: null
      };
    } else {
      // Request setup error
      return {
        message: error.message || 'Unknown error',
        status: -1,
        data: null
      };
    }
  }
  
  // Jobs API
  async getJobs(params = {}) {
    try {
      const response = await this.client.get('/api/jobs/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  async getJobBySlug(slug) {
    try {
      const response = await this.client.get(`/api/jobs/${slug}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  async getLatestJobs() {
    try {
      const response = await this.client.get('/api/jobs/latest/');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  async getRecentJobs() {
    try {
      const response = await this.client.get('/api/jobs/recent/');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  // Categories API
  async getCategories() {
    try {
      const response = await this.client.get('/api/categories/');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  async getCategoryJobs(slug) {
    try {
      const response = await this.client.get(`/api/categories/${slug}/jobs/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  // Sources API
  async getSources() {
    try {
      const response = await this.client.get('/api/sources/');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  // Analytics API
  async getDashboardStats() {
    try {
      const response = await this.client.get('/api/analytics/dashboard-stats/');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  async getPopularJobs() {
    try {
      const response = await this.client.get('/api/analytics/popular-jobs/');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  // Search API
  async searchJobs(query, params = {}) {
    try {
      const searchParams = { q: query, ...params };
      const response = await this.client.get('/api/jobs/search/', { params: searchParams });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

const apiService = new ApiService();
export default apiService;
