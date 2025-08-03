import React from 'react';

const FilterSidebar = ({ filters, onFilterChange }) => {
  const statusOptions = [
    { value: 'announced', label: 'Latest Jobs' },
    { value: 'admit_card', label: 'Admit Card' },
    { value: 'answer_key', label: 'Answer Key' },
    { value: 'result', label: 'Result' },
  ];

  const categoryOptions = [
    { value: '', label: 'All Categories' },
    { value: 'central-government', label: 'Central Government' },
    { value: 'state-government', label: 'State Government' },
    { value: 'banking-finance', label: 'Banking & Finance' },
    { value: 'railway-jobs', label: 'Railway Jobs' },
    { value: 'defense-jobs', label: 'Defense Jobs' },
    { value: 'teaching-jobs', label: 'Teaching Jobs' },
    { value: 'engineering-jobs', label: 'Engineering Jobs' },
    { value: 'medical-jobs', label: 'Medical Jobs' },
  ];

  const handleFilterChange = (key, value) => {
    onFilterChange({ [key]: value });
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
      </div>
      <div className="card-body space-y-6">
        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Job Status
          </label>
          <div className="space-y-2">
            {statusOptions.map((option) => (
              <label key={option.value} className="flex items-center">
                <input
                  type="radio"
                  name="status"
                  value={option.value}
                  checked={filters.status === option.value}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                />
                <span className="ml-3 text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Category Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Category
          </label>
          <select
            value={filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
            className="input"
          >
            {categoryOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Search Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Search Jobs
          </label>
          <input
            type="text"
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            placeholder="Search by title or organization..."
            className="input"
          />
        </div>

        {/* Clear Filters */}
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={() => onFilterChange({
              status: 'announced',
              category: '',
              source: '',
              search: '',
            })}
            className="btn btn-secondary w-full"
          >
            Clear All Filters
          </button>
        </div>
      </div>
    </div>
  );
};

export default FilterSidebar;
