'use client';

import { useState, useEffect, useMemo } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Property, PropertyFilters, apiClient } from '@/services/api';
import PropertyFiltersComponent from '@/components/PropertyFilters';
import { useLunrSearch } from '@/hooks/useLunrSearch';

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
  const [allProperties, setAllProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState<PropertyFilters>({});
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Use Lunr.js for client-side search
  const { searchQuery, setSearchQuery, filteredProperties: searchedProperties, isSearching } = useLunrSearch(allProperties);

  // Load all properties once on mount (paginate to get all)
  useEffect(() => {
    const loadAllProperties = async () => {
      try {
        setLoading(true);
        setError('');

        // Load properties in batches (backend max limit is 100)
        const allProps: Property[] = [];
        let skip = 0;
        const limit = 100;
        let hasMore = true;

        while (hasMore) {
          const response = await apiClient.getProperties({ skip, limit });
          allProps.push(...response.properties);
          hasMore = response.has_more;
          skip += limit;
        }

        setAllProperties(allProps);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load properties');
      } finally {
        setLoading(false);
      }
    };
    loadAllProperties();
  }, []);

  // Apply filters client-side
  const filteredProperties = useMemo(() => {
    let result = searchedProperties;

    // Apply filters
    if (filters.property_type) {
      result = result.filter(p => p.property_type === filters.property_type);
    }
    if (filters.status) {
      result = result.filter(p => p.status === filters.status);
    }
    if (filters.min_price !== undefined) {
      result = result.filter(p => p.price >= filters.min_price!);
    }
    if (filters.max_price !== undefined) {
      result = result.filter(p => p.price <= filters.max_price!);
    }
    if (filters.min_bedrooms !== undefined) {
      result = result.filter(p => p.bedrooms >= filters.min_bedrooms!);
    }
    if (filters.max_bedrooms !== undefined) {
      result = result.filter(p => p.bedrooms <= filters.max_bedrooms!);
    }
    if (filters.min_bathrooms !== undefined) {
      result = result.filter(p => p.bathrooms >= filters.min_bathrooms!);
    }
    if (filters.max_bathrooms !== undefined) {
      result = result.filter(p => p.bathrooms <= filters.max_bathrooms!);
    }
    if (filters.city) {
      result = result.filter(p => p.location?.city?.toLowerCase().includes(filters.city!.toLowerCase()));
    }
    if (filters.has_garage) {
      result = result.filter(p => p.features?.has_garage);
    }
    if (filters.has_pool) {
      result = result.filter(p => p.features?.has_pool);
    }
    if (filters.has_garden) {
      result = result.filter(p => p.features?.has_garden);
    }
    if (filters.pet_friendly) {
      result = result.filter(p => p.features?.pet_friendly);
    }

    // Apply sorting
    result = [...result].sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'price':
          comparison = a.price - b.price;
          break;
        case 'bedrooms':
          comparison = a.bedrooms - b.bedrooms;
          break;
        case 'area':
          comparison = a.area - b.area;
          break;
        case 'created_at':
        default:
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [searchedProperties, filters, sortBy, sortOrder]);

  const handleFiltersChange = (newFilters: PropertyFilters) => {
    setFilters(newFilters);
  };

  const handleFiltersReset = () => {
    setFilters({});
    setSearchQuery('');
  };

  const handleSortChange = (newSortBy: string, newSortOrder: 'asc' | 'desc') => {
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);
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

        {/* Search Bar - Instant search with Lunr.js */}
        <div className="mb-8">
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search properties by title, description, or location..."
                className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              {isSearching && (
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
                </div>
              )}
            </div>
            {searchQuery && (
              <p className="text-sm text-gray-500 mt-2 text-center">
                Found {filteredProperties.length} result{filteredProperties.length !== 1 ? 's' : ''} for &quot;{searchQuery}&quot;
              </p>
            )}
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
            {filteredProperties.length > 0 ? (
              <>
                Showing {filteredProperties.length} properties
                {Object.keys(filters).length > 0 || searchQuery ? ' (filtered)' : ''}
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
        {filteredProperties.length === 0 && !loading ? (
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredProperties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
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
    if (!property.location) {
      return 'Location not specified';
    }
    if (typeof property.location === 'string') {
      return property.location;
    }
    const city = property.location.city || '';
    const state = property.location.state || '';
    if (city && state) {
      return `${city}, ${state}`;
    }
    return city || state || 'Location not specified';
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
            {typeof property.property_type === 'string' ? property.property_type : 'Property'}
          </span>
        </div>
        <div className="absolute top-4 left-4">
          <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
            property.status === 'available' ? 'bg-green-100 text-green-800' :
            property.status === 'sold' ? 'bg-red-100 text-red-800' :
            property.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {typeof property.status === 'string' ? property.status.charAt(0).toUpperCase() + property.status.slice(1) : 'Available'}
          </span>
        </div>
      </div>
      <div className="p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {typeof property.title === 'string' ? property.title : 'Untitled Property'}
        </h3>
        <p className="text-gray-600 mb-4">{getLocationString()}</p>
        <div className="flex justify-between items-center mb-4">
          <span className="text-2xl font-bold text-blue-600">
            ${typeof property.price === 'number' ? property.price.toLocaleString() : '0'}
          </span>
          <div className="flex gap-2 text-sm text-gray-500">
            {property.bedrooms > 0 && (
              <>
                <span>{property.bedrooms} beds</span>
                <span>•</span>
              </>
            )}
            {property.bathrooms > 0 && (
              <>
                <span>{property.bathrooms} baths</span>
                <span>•</span>
              </>
            )}
            <span>{typeof property.area === 'number' ? property.area.toLocaleString() : '0'} sq ft</span>
          </div>
        </div>

        {/* Property Features */}
        {property.features && typeof property.features === 'object' && (
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

        <p className="text-gray-600 mb-4 line-clamp-2">
          {typeof property.description === 'string' ? property.description : ''}
        </p>
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