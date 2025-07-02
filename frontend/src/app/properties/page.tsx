'use client';

import { useState, useEffect, useCallback } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Property, PropertyFilters, PropertyResponse, apiClient } from '@/services/api';
import PropertyFiltersComponent from '@/components/PropertyFilters';

const PLACEHOLDER_IMAGE = 'https://images.unsplash.com/photo-1582407947304-fd86f028f716?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80';

const isValidUrl = (url: string) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export default function PropertiesPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState<PropertyFilters>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [inputValue, setInputValue] = useState('');
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 12,
    total: 0,
    hasMore: false
  });
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Debounced search effect
  useEffect(() => {
    const timer = setTimeout(() => {
      if (inputValue !== searchQuery) {
        setSearchQuery(inputValue);
        setPagination(prev => ({ ...prev, skip: 0 }));
      }
    }, 500); // 500ms delay

    return () => clearTimeout(timer);
  }, [inputValue, searchQuery]);

  const loadProperties = useCallback(async (newFilters?: PropertyFilters, newSkip = 0) => {
    try {
      setLoading(true);
      setError('');

      let response: PropertyResponse;

      if (searchQuery.trim()) {
        // Use search endpoint
        response = await apiClient.searchProperties(searchQuery, {
          skip: newSkip,
          limit: pagination.limit
        });
      } else {
        // Use filtered listing endpoint
        response = await apiClient.getProperties({
          skip: newSkip,
          limit: pagination.limit,
          filters: newFilters || filters,
          sort_by: sortBy,
          sort_order: sortOrder
        });
      }

      if (newSkip === 0) {
        setProperties(response.properties);
      } else {
        setProperties(prev => [...prev, ...response.properties]);
      }

      setPagination({
        skip: response.skip,
        limit: response.limit,
        total: response.total,
        hasMore: response.has_more
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load properties');
    } finally {
      setLoading(false);
    }
  }, [filters, searchQuery, sortBy, sortOrder, pagination.limit]);

  // Load properties when dependencies change
  useEffect(() => {
    loadProperties(filters, 0);
  }, [filters, searchQuery, sortBy, sortOrder, loadProperties]);

  const handleFiltersChange = (newFilters: PropertyFilters) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const handleFiltersReset = () => {
    setFilters({});
    setSearchQuery('');
    setInputValue('');
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setInputValue(query);
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const handleLoadMore = () => {
    const newSkip = pagination.skip + pagination.limit;
    loadProperties(filters, newSkip);
  };

  const handleSortChange = (newSortBy: string, newSortOrder: 'asc' | 'desc') => {
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
            <p className="mt-2 text-gray-600">Loading properties...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-block p-4 rounded-full bg-red-100 text-red-600 mb-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-red-600">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Available Properties</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Explore our collection of premium properties in prime locations
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch(inputValue)}
                placeholder="Search properties by title, description, or location..."
                className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <button
                onClick={() => handleSearch(inputValue)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <span className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                  Search
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Filters */}
        <PropertyFiltersComponent
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onReset={handleFiltersReset}
        />

        {/* Results Header */}
        <div className="flex flex-wrap justify-between items-center mb-6">
          <div className="text-gray-600">
            {pagination.total > 0 ? (
              <>
                Showing {properties.length} of {pagination.total} properties
                {Object.keys(filters).length > 0 || searchQuery || inputValue ? ' (filtered)' : ''}
              </>
            ) : (
              'No properties found'
            )}
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600">Sort by:</label>
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={(e) => {
                  const [field, order] = e.target.value.split('-');
                  handleSortChange(field, order as 'asc' | 'desc');
                }}
                className="px-3 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="created_at-desc">Newest First</option>
                <option value="created_at-asc">Oldest First</option>
                <option value="price-asc">Price: Low to High</option>
                <option value="price-desc">Price: High to Low</option>
                <option value="bedrooms-desc">Most Bedrooms</option>
                <option value="area-desc">Largest Area</option>
              </select>
            </div>
          </div>
        </div>
        
        {/* Properties Grid */}
        {properties.length === 0 && !loading ? (
          <div className="text-center py-12">
            <div className="inline-block p-4 rounded-full bg-gray-100 text-gray-400 mb-4">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H9m0 0H5m0 0h2M7 7h.01M7 3h.01" />
              </svg>
            </div>
            <p className="text-gray-600 mb-4">No properties match your search criteria.</p>
            <button
              onClick={handleFiltersReset}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {properties.map((property) => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>

            {/* Load More Button */}
            {pagination.hasMore && (
              <div className="text-center mt-12">
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Loading...' : 'Load More Properties'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// Property Card Component
function PropertyCard({ property }: { property: Property }) {
  const getImageUrl = () => {
    if (property.media?.images && property.media.images.length > 0 && isValidUrl(property.media.images[0])) {
      return property.media.images[0];
    }
    return PLACEHOLDER_IMAGE;
  };

  const getLocationString = () => {
    if (typeof property.location === 'string') {
      return property.location;
    }
    return `${property.location.city}, ${property.location.state}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
      <div className="relative h-48">
        <Image
          src={getImageUrl()}
          alt={property.title}
          fill
          style={{ objectFit: 'cover' }}
        />
        <div className="absolute top-4 right-4">
          <span className="px-3 py-1 bg-blue-600 text-white text-sm font-semibold rounded-full capitalize">
            {property.property_type}
          </span>
        </div>
        <div className="absolute top-4 left-4">
          <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
            property.status === 'available' ? 'bg-green-100 text-green-800' :
            property.status === 'sold' ? 'bg-red-100 text-red-800' :
            property.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {property.status.charAt(0).toUpperCase() + property.status.slice(1)}
          </span>
        </div>
      </div>
      <div className="p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{property.title}</h3>
        <p className="text-gray-600 mb-4">{getLocationString()}</p>
        <div className="flex justify-between items-center mb-4">
          <span className="text-2xl font-bold text-blue-600">
            ${property.price.toLocaleString()}
          </span>
          <div className="flex gap-2 text-sm text-gray-500">
            <span>{property.bedrooms} beds</span>
            <span>•</span>
            <span>{property.bathrooms} baths</span>
            <span>•</span>
            <span>{property.area.toLocaleString()} sq ft</span>
          </div>
        </div>
        
        {/* Property Features */}
        {property.features && (
          <div className="flex flex-wrap gap-2 mb-4">
            {property.features.has_garage && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">Garage</span>
            )}
            {property.features.has_pool && (
              <span className="px-2 py-1 bg-blue-100 text-blue-600 text-xs rounded">Pool</span>
            )}
            {property.features.has_garden && (
              <span className="px-2 py-1 bg-green-100 text-green-600 text-xs rounded">Garden</span>
            )}
            {property.features.pet_friendly && (
              <span className="px-2 py-1 bg-purple-100 text-purple-600 text-xs rounded">Pet Friendly</span>
            )}
          </div>
        )}

        <p className="text-gray-600 mb-4 line-clamp-2">{property.description}</p>
        <Link
          href={`/properties/${property.id}`}
          className="block w-full bg-blue-600 text-white text-center py-2 rounded hover:bg-blue-700 transition-colors"
        >
          View Details
        </Link>
      </div>
    </div>
  );
} 