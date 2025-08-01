/**
 * Sentry configuration for SarkariBot frontend
 */
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

/**
 * Initialize Sentry for error tracking and performance monitoring
 */
export const initSentry = () => {
  const dsn = process.env.REACT_APP_SENTRY_DSN;
  
  if (!dsn) {
    console.warn('Sentry DSN not configured, error tracking disabled');
    return;
  }

  Sentry.init({
    dsn,
    integrations: [
      new BrowserTracing({
        // Set up automatic route change tracking for React Router
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          React.useEffect,
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes
        ),
      }),
    ],
    
    // Performance monitoring
    tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
    
    // Environment
    environment: process.env.NODE_ENV,
    
    // Release tracking
    release: process.env.REACT_APP_VERSION || '1.0.0',
    
    // Error filtering
    beforeSend(event, hint) {
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
    
    // Capture console errors
    debug: process.env.NODE_ENV === 'development',
  });
  
  // Set user context if available
  const setUserContext = (user) => {
    Sentry.setUser({
      id: user.id,
      email: user.email,
      // Don't include sensitive information
    });
  };
  
  // Set extra context
  Sentry.setContext('device', {
    name: navigator.platform,
    family: navigator.userAgent,
    model: navigator.vendor,
  });
  
  console.log('Sentry initialized for error tracking');
  
  return { setUserContext };
};

/**
 * Manually capture exception
 */
export const captureException = (error, context = {}) => {
  Sentry.withScope((scope) => {
    // Add extra context
    Object.keys(context).forEach(key => {
      scope.setContext(key, context[key]);
    });
    
    Sentry.captureException(error);
  });
};

/**
 * Manually capture message
 */
export const captureMessage = (message, level = 'info', context = {}) => {
  Sentry.withScope((scope) => {
    scope.setLevel(level);
    
    // Add extra context
    Object.keys(context).forEach(key => {
      scope.setContext(key, context[key]);
    });
    
    Sentry.captureMessage(message);
  });
};

/**
 * Add breadcrumb
 */
export const addBreadcrumb = (message, category = 'navigation', level = 'info', data = {}) => {
  Sentry.addBreadcrumb({
    message,
    category,
    level,
    data,
    timestamp: Date.now() / 1000,
  });
};

/**
 * HOC for capturing component errors
 */
export const withErrorBoundary = (Component, options = {}) => {
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
};

export default Sentry;