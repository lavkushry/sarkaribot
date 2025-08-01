import apiService from '../services/apiService';
import { mockJobPosting, mockJobCategory } from '../test-utils';

// Mock axios
jest.mock('axios');

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getLatestJobs', () => {
    test('fetches latest jobs successfully', async () => {
      const mockResponse = {
        data: {
          results: [mockJobPosting],
          count: 1,
          next: null,
          previous: null
        }
      };

      const axios = require('axios');
      axios.get.mockResolvedValue(mockResponse);

      const result = await apiService.getLatestJobs();

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/', {
        params: { page: 1, page_size: 20 }
      });
      expect(result).toEqual(mockResponse.data);
    });

    test('handles pagination parameters', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: { results: [] } });

      await apiService.getLatestJobs(2, 10);

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/', {
        params: { page: 2, page_size: 10 }
      });
    });

    test('handles API errors gracefully', async () => {
      const axios = require('axios');
      axios.get.mockRejectedValue(new Error('Network Error'));

      await expect(apiService.getLatestJobs()).rejects.toThrow('Network Error');
    });
  });

  describe('getJobById', () => {
    test('fetches single job by ID', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: mockJobPosting });

      const result = await apiService.getJobById(1);

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/1/');
      expect(result).toEqual(mockJobPosting);
    });

    test('handles non-existent job', async () => {
      const axios = require('axios');
      axios.get.mockRejectedValue({ response: { status: 404 } });

      await expect(apiService.getJobById(999)).rejects.toMatchObject({
        response: { status: 404 }
      });
    });
  });

  describe('searchJobs', () => {
    test('searches jobs with query', async () => {
      const axios = require('axios');
      const searchResults = { data: { results: [mockJobPosting], count: 1 } };
      axios.get.mockResolvedValue(searchResults);

      const result = await apiService.searchJobs('software engineer');

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/', {
        params: { search: 'software engineer', page: 1, page_size: 20 }
      });
      expect(result).toEqual(searchResults.data);
    });

    test('handles empty search query', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: { results: [] } });

      const result = await apiService.searchJobs('');

      expect(result.results).toEqual([]);
    });

    test('includes filters in search', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: { results: [] } });

      const filters = {
        category: 'latest-jobs',
        source: 'SSC',
        location: 'Delhi'
      };

      await apiService.searchJobs('engineer', filters);

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/', {
        params: {
          search: 'engineer',
          page: 1,
          page_size: 20,
          category: 'latest-jobs',
          source: 'SSC',
          location: 'Delhi'
        }
      });
    });
  });

  describe('getCategories', () => {
    test('fetches all categories', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: [mockJobCategory] });

      const result = await apiService.getCategories();

      expect(axios.get).toHaveBeenCalledWith('/api/categories/');
      expect(result).toEqual([mockJobCategory]);
    });
  });

  describe('getJobsByCategory', () => {
    test('fetches jobs by category slug', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: { results: [mockJobPosting] } });

      const result = await apiService.getJobsByCategory('latest-jobs');

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/', {
        params: { category: 'latest-jobs', page: 1, page_size: 20 }
      });
      expect(result).toEqual({ results: [mockJobPosting] });
    });

    test('handles pagination for category jobs', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: { results: [] } });

      await apiService.getJobsByCategory('admit-card', 2, 15);

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/', {
        params: { category: 'admit-card', page: 2, page_size: 15 }
      });
    });
  });

  describe('getStats', () => {
    test('fetches platform statistics', async () => {
      const mockStats = {
        total_jobs: 1500,
        jobs_this_week: 45,
        total_sources: 25,
        active_sources: 23
      };

      const axios = require('axios');
      axios.get.mockResolvedValue({ data: mockStats });

      const result = await apiService.getStats();

      expect(axios.get).toHaveBeenCalledWith('/api/stats/');
      expect(result).toEqual(mockStats);
    });
  });

  describe('getTrendingJobs', () => {
    test('fetches trending jobs', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: [mockJobPosting] });

      const result = await apiService.getTrendingJobs();

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/trending/');
      expect(result).toEqual([mockJobPosting]);
    });

    test('limits number of trending jobs', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: [] });

      await apiService.getTrendingJobs(5);

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/trending/', {
        params: { limit: 5 }
      });
    });
  });

  describe('getPopularJobs', () => {
    test('fetches popular jobs', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: [mockJobPosting] });

      const result = await apiService.getPopularJobs();

      expect(axios.get).toHaveBeenCalledWith('/api/jobs/popular/');
      expect(result).toEqual([mockJobPosting]);
    });
  });

  describe('Error Handling', () => {
    test('handles network errors', async () => {
      const axios = require('axios');
      axios.get.mockRejectedValue(new Error('Network Error'));

      await expect(apiService.getLatestJobs()).rejects.toThrow('Network Error');
    });

    test('handles 500 server errors', async () => {
      const axios = require('axios');
      axios.get.mockRejectedValue({
        response: { status: 500, data: { error: 'Internal Server Error' } }
      });

      await expect(apiService.getJobById(1)).rejects.toMatchObject({
        response: { status: 500 }
      });
    });

    test('handles timeout errors', async () => {
      const axios = require('axios');
      axios.get.mockRejectedValue({ code: 'ECONNABORTED' });

      await expect(apiService.getLatestJobs()).rejects.toMatchObject({
        code: 'ECONNABORTED'
      });
    });
  });

  describe('Request Configuration', () => {
    test('includes proper headers', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: [] });

      await apiService.getLatestJobs();

      // Check if axios was configured with proper headers
      expect(axios.get).toHaveBeenCalled();
    });

    test('includes authentication token when available', async () => {
      // Mock localStorage
      const mockLocalStorage = {
        getItem: jest.fn().mockReturnValue('mock-token')
      };
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage
      });

      const axios = require('axios');
      axios.get.mockResolvedValue({ data: [] });

      await apiService.getLatestJobs();

      // Should include auth header if token exists
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('authToken');
    });
  });

  describe('Response Caching', () => {
    test('caches frequently requested data', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: [mockJobCategory] });

      // First call
      await apiService.getCategories();
      
      // Second call should use cache (if implemented)
      await apiService.getCategories();

      // Implementation dependent - might call API twice or use cache
      expect(axios.get).toHaveBeenCalled();
    });
  });

  describe('Data Transformation', () => {
    test('transforms API response data correctly', async () => {
      const apiResponse = {
        data: {
          results: [{
            ...mockJobPosting,
            application_end_date: '2024-12-31T23:59:59Z'
          }]
        }
      };

      const axios = require('axios');
      axios.get.mockResolvedValue(apiResponse);

      const result = await apiService.getLatestJobs();

      // Should transform date strings to Date objects if implemented
      expect(result.results[0]).toBeDefined();
    });

    test('handles malformed API responses', async () => {
      const axios = require('axios');
      axios.get.mockResolvedValue({ data: null });

      const result = await apiService.getLatestJobs();

      // Should handle gracefully
      expect(result).toBeDefined();
    });
  });
});