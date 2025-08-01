/**
 * Monitoring utilities for frontend error tracking and performance monitoring
 */

class Monitor {
  constructor() {
    this.performanceEntries = [];
    this.errorCount = 0;
    this.initialized = false;
  }

  /**
   * Initialize monitoring
   */
  init(config = {}) {
    if (this.initialized) return;

    this.config = {
      apiEndpoint: '/api/v1/monitoring',
      enablePerformanceTracking: true,
      enableErrorTracking: true,
      enableUserTracking: true,
      sampleRate: 0.1, // 10% sampling for performance
      ...config
    };

    this.setupErrorTracking();
    this.setupPerformanceTracking();
    this.setupUnhandledPromiseRejection();
    this.setupNavigationTracking();
    
    this.initialized = true;
    console.log('Frontend monitoring initialized');
  }

  /**
   * Setup global error tracking
   */
  setupErrorTracking() {
    if (!this.config.enableErrorTracking) return;

    // Global error handler
    window.addEventListener('error', (event) => {
      this.logError({
        type: 'javascript_error',
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack,
        timestamp: new Date().toISOString(),
        url: window.location.href
      });
    });

    // Resource loading errors
    window.addEventListener('error', (event) => {
      if (event.target !== window) {
        this.logError({
          type: 'resource_error',
          message: `Failed to load resource: ${event.target.src || event.target.href}`,
          element: event.target.tagName,
          url: window.location.href,
          timestamp: new Date().toISOString()
        });
      }
    }, true);
  }

  /**
   * Setup unhandled promise rejection tracking
   */
  setupUnhandledPromiseRejection() {
    window.addEventListener('unhandledrejection', (event) => {
      this.logError({
        type: 'unhandled_promise_rejection',
        message: event.reason?.message || 'Unhandled promise rejection',
        stack: event.reason?.stack,
        timestamp: new Date().toISOString(),
        url: window.location.href
      });
    });
  }

  /**
   * Setup performance tracking
   */
  setupPerformanceTracking() {
    if (!this.config.enablePerformanceTracking) return;

    // Page load performance
    window.addEventListener('load', () => {
      setTimeout(() => {
        this.trackPageLoadPerformance();
      }, 0);
    });

    // Web Vitals tracking
    this.trackWebVitals();
  }

  /**
   * Setup navigation tracking
   */
  setupNavigationTracking() {
    // Track page visibility changes
    document.addEventListener('visibilitychange', () => {
      this.trackEvent('page_visibility_change', {
        visible: !document.hidden,
        timestamp: new Date().toISOString()
      });
    });

    // Track beforeunload for session duration
    window.addEventListener('beforeunload', () => {
      this.trackEvent('page_unload', {
        duration: Date.now() - this.pageStartTime,
        timestamp: new Date().toISOString()
      });
    });

    this.pageStartTime = Date.now();
  }

  /**
   * Track page load performance
   */
  trackPageLoadPerformance() {
    if (!performance.getEntriesByType) return;

    const navigation = performance.getEntriesByType('navigation')[0];
    if (!navigation) return;

    const metrics = {
      loadTime: navigation.loadEventEnd - navigation.fetchStart,
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
      firstByte: navigation.responseStart - navigation.requestStart,
      domProcessing: navigation.domComplete - navigation.domLoading,
      resourceCount: performance.getEntriesByType('resource').length
    };

    this.trackPerformance('page_load', metrics);
  }

  /**
   * Track Web Vitals (Core Web Vitals)
   */
  trackWebVitals() {
    // First Contentful Paint
    this.observePerformanceEntry('paint', (entries) => {
      entries.forEach(entry => {
        if (entry.name === 'first-contentful-paint') {
          this.trackPerformance('first_contentful_paint', {
            value: entry.startTime,
            unit: 'ms'
          });
        }
      });
    });

    // Largest Contentful Paint
    this.observePerformanceEntry('largest-contentful-paint', (entries) => {
      const lastEntry = entries[entries.length - 1];
      this.trackPerformance('largest_contentful_paint', {
        value: lastEntry.startTime,
        unit: 'ms'
      });
    });

    // First Input Delay (approximation)
    this.observePerformanceEntry('first-input', (entries) => {
      entries.forEach(entry => {
        this.trackPerformance('first_input_delay', {
          value: entry.processingStart - entry.startTime,
          unit: 'ms'
        });
      });
    });

    // Cumulative Layout Shift
    this.observePerformanceEntry('layout-shift', (entries) => {
      let clsValue = 0;
      entries.forEach(entry => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      });
      
      if (clsValue > 0) {
        this.trackPerformance('cumulative_layout_shift', {
          value: clsValue,
          unit: 'score'
        });
      }
    });
  }

  /**
   * Observe performance entries
   */
  observePerformanceEntry(type, callback) {
    if (!PerformanceObserver) return;

    try {
      const observer = new PerformanceObserver((list) => {
        callback(list.getEntries());
      });
      observer.observe({ entryTypes: [type] });
    } catch (e) {
      console.warn(`Performance observer for ${type} not supported`);
    }
  }

  /**
   * Log an error
   */
  logError(errorData) {
    this.errorCount++;
    
    const error = {
      ...errorData,
      sessionId: this.getSessionId(),
      userId: this.getUserId(),
      browserInfo: this.getBrowserInfo(),
      pageInfo: this.getPageInfo()
    };

    // Send to backend
    this.sendToBackend('/feedback/', {
      type: 'error_feedback',
      message: error.message,
      page_url: window.location.href,
      user_data: error,
      browser_info: error.browserInfo
    });

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Frontend Error:', error);
    }
  }

  /**
   * Track performance metric
   */
  trackPerformance(metric, data) {
    // Sample performance data to avoid overwhelming the backend
    if (Math.random() > this.config.sampleRate) return;

    const performanceData = {
      metric,
      value: data.value || data,
      unit: data.unit || 'ms',
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId(),
      pageInfo: this.getPageInfo()
    };

    this.performanceEntries.push(performanceData);

    // Send in batches
    if (this.performanceEntries.length >= 10) {
      this.flushPerformanceData();
    }
  }

  /**
   * Track custom event
   */
  trackEvent(eventName, data = {}) {
    const event = {
      event: eventName,
      data,
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId(),
      pageInfo: this.getPageInfo()
    };

    this.sendToBackend('/feedback/', {
      type: 'suggestion',
      message: `Event: ${eventName}`,
      page_url: window.location.href,
      user_data: event
    });
  }

  /**
   * Flush performance data to backend
   */
  flushPerformanceData() {
    if (this.performanceEntries.length === 0) return;

    this.sendToBackend('/feedback/', {
      type: 'suggestion',
      message: 'Performance Metrics',
      page_url: window.location.href,
      user_data: {
        type: 'performance_batch',
        metrics: this.performanceEntries
      }
    });

    this.performanceEntries = [];
  }

  /**
   * Send data to backend
   */
  async sendToBackend(endpoint, data) {
    try {
      await fetch(`${this.config.apiEndpoint}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });
    } catch (error) {
      console.error('Failed to send monitoring data:', error);
    }
  }

  /**
   * Get session ID
   */
  getSessionId() {
    let sessionId = sessionStorage.getItem('monitoring_session_id');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('monitoring_session_id', sessionId);
    }
    return sessionId;
  }

  /**
   * Get user ID (if available)
   */
  getUserId() {
    // Implement based on your authentication system
    return localStorage.getItem('user_id') || null;
  }

  /**
   * Get browser information
   */
  getBrowserInfo() {
    return {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      onLine: navigator.onLine,
      screen: {
        width: window.screen.width,
        height: window.screen.height,
        colorDepth: window.screen.colorDepth
      },
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };
  }

  /**
   * Get page information
   */
  getPageInfo() {
    return {
      url: window.location.href,
      title: document.title,
      referrer: document.referrer,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get error statistics
   */
  getErrorStats() {
    return {
      errorCount: this.errorCount,
      sessionDuration: Date.now() - this.pageStartTime
    };
  }
}

// Create global monitor instance
const monitor = new Monitor();

export default monitor;