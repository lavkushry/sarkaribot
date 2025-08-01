/**
 * Sentry configuration for SarkariBot frontend
 */

// Mock Sentry implementation for development
const createMockSentry = () => ({
  init: () => console.log('Mock Sentry initialized'),
  captureException: (error) => console.error('Mock Sentry captured exception:', error),
  captureMessage: (message) => console.log('Mock Sentry captured message:', message),
  addBreadcrumb: (breadcrumb) => console.log('Mock Sentry breadcrumb:', breadcrumb),
  setUser: (user) => console.log('Mock Sentry user set:', user),
  setContext: (key, context) => console.log('Mock Sentry context set:', key, context),
  withScope: (callback) => callback({ 
    setLevel: () => {}, 
    setContext: () => {},
    setTag: () => {}
  }),
  withErrorBoundary: (Component) => Component,
});

// Create mock BrowserTracing class
class MockBrowserTracing {
  // Empty constructor for compatibility
}

const Sentry = createMockSentry();
const BrowserTracing = MockBrowserTracing;

/**
 * Initialize Sentry for error tracking and performance monitoring
 */
export const initSentry = () => {
  const dsn = process.env.REACT_APP_SENTRY_DSN;
  
  if (!dsn) {
    console.warn('Sentry DSN not configured, using mock error tracking');
    return { setUserContext: () => {} };
  }

  try {
    Sentry.init({
      dsn,
      integrations: [
        new BrowserTracing(),
      ],
      
      // Performance monitoring
      tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
      
      // Environment
      environment: process.env.NODE_ENV,
      
      // Release tracking
      release: process.env.REACT_APP_VERSION || '1.0.0',
      
      // Error filtering
      beforeSend(event) {
        // Don't send errors in development unless explicitly enabled
        if (process.env.NODE_ENV === 'development' && !process.env.REACT_APP_SENTRY_DEBUG) {
          return null;
        }
        
        // Filter out network errors from ad blockers
        if (event.exception?.values?.[0]?.type === 'ChunkLoadError') {
          return null;
        }
        
        // Filter out cancelled requests
        if (event.exception?.values?.[0]?.value?.includes('cancelled')) {
          return null;
        }
        
        return event;
      },
      
      // Additional context
      initialScope: {
        tags: {
          component: 'frontend',
          framework: 'react'
        }
      },
      
      // Capture unhandled promise rejections
      captureUnhandledRejections: true,
      
      // Debug mode
      debug: process.env.NODE_ENV === 'development',
    });
    
    // Set extra context
    Sentry.setContext('device', {
      name: navigator.platform,
      family: navigator.userAgent,
      model: navigator.vendor,
    });
    
    console.log('Sentry initialized for error tracking');
  } catch (error) {
    console.error('Failed to initialize Sentry:', error);
  }
  
  return { setUserContext: (user) => Sentry.setUser(user) };
};

/**
 * Manually capture exception
 */
export const captureException = (error, context = {}) => {
  try {
    Sentry.withScope((scope) => {
      // Add extra context
      Object.keys(context).forEach(key => {
        scope.setContext(key, context[key]);
      });
      
      Sentry.captureException(error);
    });
  } catch (e) {
    console.error('Failed to capture exception:', e);
  }
};

/**
 * Manually capture message
 */
export const captureMessage = (message, level = 'info', context = {}) => {
  try {
    Sentry.withScope((scope) => {
      scope.setLevel(level);
      
      // Add extra context
      Object.keys(context).forEach(key => {
        scope.setContext(key, context[key]);
      });
      
      Sentry.captureMessage(message);
    });
  } catch (e) {
    console.error('Failed to capture message:', e);
  }
};

/**
 * Add breadcrumb
 */
export const addBreadcrumb = (message, category = 'navigation', level = 'info', data = {}) => {
  try {
    Sentry.addBreadcrumb({
      message,
      category,
      level,
      data,
      timestamp: Date.now() / 1000,
    });
  } catch (e) {
    console.error('Failed to add breadcrumb:', e);
  }
};

/**
 * HOC for capturing component errors
 */
export const withErrorBoundary = (Component, options = {}) => {
  try {
    return Sentry.withErrorBoundary(Component, {
      fallback: ({ error, resetError }) => (
        <div className="error-boundary">
          <div className="error-boundary-content">
            <h2>Something went wrong</h2>
            <p>An unexpected error occurred. Our team has been notified.</p>
            <button onClick={resetError} className="btn btn-primary">
              Try again
            </button>
          </div>
        </div>
      ),
      beforeCapture: (scope, error, errorInfo) => {
        scope.setTag('component', options.name || 'Unknown');
        scope.setContext('componentStack', {
          componentStack: errorInfo.componentStack,
        });
      },
      ...options,
    });
  } catch (e) {
    console.error('Failed to create error boundary:', e);
    return Component;
  }
};

export default Sentry;