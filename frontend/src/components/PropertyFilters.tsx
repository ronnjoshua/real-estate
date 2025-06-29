'use client';

import { useState, useEffect, useCallback } from 'react';
import { PropertyFilters as PropertyFiltersType } from '../services/api';

interface PropertyFiltersProps {
  filters: PropertyFiltersType;
  onFiltersChange: (filters: PropertyFiltersType) => void;
  onReset: () => void;
}

const PropertyFilters = ({ filters, onFiltersChange, onReset }: PropertyFiltersProps) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [localFilters, setLocalFilters] = useState<PropertyFiltersType>(filters);

  const propertyTypes = [
    { value: 'house', label: 'House' },
    { value: 'apartment', label: 'Apartment' },
    { value: 'condo', label: 'Condo' },
    { value: 'townhouse', label: 'Townhouse' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'land', label: 'Land' }
  ];

  const statusOptions = [
    { value: 'available', label: 'Available' },
    { value: 'sold', label: 'Sold' },
    { value: 'rented', label: 'Rented' },
    { value: 'pending', label: 'Pending' }
  ];

  const bedroomOptions = Array.from({ length: 11 }, (_, i) => ({ value: i, label: i === 0 ? 'Studio' : `${i}+` }));
  const bathroomOptions = Array.from({ length: 11 }, (_, i) => ({ value: i, label: `${i}+` }));

  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 50 }, (_, i) => currentYear - i);

  // Sync local filters with parent filters
  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  // Debounced update effect for text fields
  useEffect(() => {
    const timer = setTimeout(() => {
      onFiltersChange(localFilters);
    }, 500);

    return () => clearTimeout(timer);
  }, [localFilters, onFiltersChange]);

  const updateFilter = (key: keyof PropertyFiltersType, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const updateLocalFilter = (key: keyof PropertyFiltersType, value: any) => {
    setLocalFilters(prev => ({ ...prev, [key]: value }));
  };

  const hasActiveFilters = Object.values(filters).some(value => value !== undefined && value !== null && value !== '');

  const handleReset = () => {
    setLocalFilters({});
    onReset();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-8">
      {/* Basic Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Property Type
          </label>
          <select
            value={filters.property_type || ''}
            onChange={(e) => updateFilter('property_type', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            {propertyTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            value={filters.status || ''}
            onChange={(e) => updateFilter('status', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            {statusOptions.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Price
          </label>
          <input
            type="number"
            value={localFilters.min_price || ''}
            onChange={(e) => updateLocalFilter('min_price', e.target.value ? parseFloat(e.target.value) : undefined)}
            placeholder="Min Price"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max Price
          </label>
          <input
            type="number"
            value={localFilters.max_price || ''}
            onChange={(e) => updateLocalFilter('max_price', e.target.value ? parseFloat(e.target.value) : undefined)}
            placeholder="Max Price"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Location Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            City
          </label>
          <input
            type="text"
            value={localFilters.city || ''}
            onChange={(e) => updateLocalFilter('city', e.target.value || undefined)}
            placeholder="Enter city"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            State
          </label>
          <input
            type="text"
            value={localFilters.state || ''}
            onChange={(e) => updateLocalFilter('state', e.target.value || undefined)}
            placeholder="Enter state"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Zip Code
          </label>
          <input
            type="text"
            value={localFilters.zip_code || ''}
            onChange={(e) => updateLocalFilter('zip_code', e.target.value || undefined)}
            placeholder="Enter zip code"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Advanced Filters Toggle */}
      <div className="mb-4">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center text-blue-600 hover:text-blue-700 font-medium"
        >
          <span>Advanced Filters</span>
          <svg
            className={`ml-1 h-4 w-4 transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="border-t pt-4">
          {/* Bedrooms and Bathrooms */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Bedrooms
              </label>
              <select
                value={filters.min_bedrooms || ''}
                onChange={(e) => updateFilter('min_bedrooms', e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any</option>
                {bedroomOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Bedrooms
              </label>
              <select
                value={filters.max_bedrooms || ''}
                onChange={(e) => updateFilter('max_bedrooms', e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any</option>
                {bedroomOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Bathrooms
              </label>
              <select
                value={filters.min_bathrooms || ''}
                onChange={(e) => updateFilter('min_bathrooms', e.target.value ? parseFloat(e.target.value) : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any</option>
                {bathroomOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Bathrooms
              </label>
              <select
                value={filters.max_bathrooms || ''}
                onChange={(e) => updateFilter('max_bathrooms', e.target.value ? parseFloat(e.target.value) : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any</option>
                {bathroomOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Area Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Area (sq ft)
              </label>
              <input
                type="number"
                value={localFilters.min_area || ''}
                onChange={(e) => updateLocalFilter('min_area', e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="Min area"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Area (sq ft)
              </label>
              <input
                type="number"
                value={localFilters.max_area || ''}
                onChange={(e) => updateLocalFilter('max_area', e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="Max area"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Year Built Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Year Built (From)
              </label>
              <select
                value={filters.year_built_min || ''}
                onChange={(e) => updateFilter('year_built_min', e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any</option>
                {yearOptions.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Year Built (To)
              </label>
              <select
                value={filters.year_built_max || ''}
                onChange={(e) => updateFilter('year_built_max', e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any</option>
                {yearOptions.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Feature Checkboxes */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.has_garage || false}
                onChange={(e) => updateFilter('has_garage', e.target.checked || undefined)}
                className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Has Garage</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.has_pool || false}
                onChange={(e) => updateFilter('has_pool', e.target.checked || undefined)}
                className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Has Pool</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.has_garden || false}
                onChange={(e) => updateFilter('has_garden', e.target.checked || undefined)}
                className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Has Garden</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.pet_friendly || false}
                onChange={(e) => updateFilter('pet_friendly', e.target.checked || undefined)}
                className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Pet Friendly</span>
            </label>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-4 border-t">
        {hasActiveFilters && (
          <button
            onClick={handleReset}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Clear All
          </button>
        )}
        <div className="text-sm text-gray-500 py-2">
          {hasActiveFilters ? 'Filters applied' : 'No filters applied'}
        </div>
      </div>
    </div>
  );
};

export default PropertyFilters; 