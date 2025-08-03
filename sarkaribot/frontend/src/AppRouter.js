import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import HomePage from './pages/HomePage';
import JobsPage from './pages/JobsPage';
import JobDetailPage from './pages/JobDetailPage';
import CategoriesPage from './pages/CategoriesPage';
import CategoryJobsPage from './pages/CategoryJobsPage';
import SearchPage from './pages/SearchPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/jobs/:slug" element={<JobDetailPage />} />
            <Route path="/categories" element={<CategoriesPage />} />
            <Route path="/category/:slug" element={<CategoryJobsPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

// 404 Page Component
const NotFoundPage = () => (
  <div className="min-h-96 flex items-center justify-center px-4">
    <div className="text-center">
      <div className="text-6xl font-bold text-gray-400 mb-4">404</div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Page not found</h1>
      <p className="text-gray-600 mb-8">
        Sorry, we couldn't find the page you're looking for.
      </p>
      <a
        href="/"
        className="btn btn-primary"
      >
        Go back home
      </a>
    </div>
  </div>
);

export default App;
