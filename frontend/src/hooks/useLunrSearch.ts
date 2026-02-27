'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import lunr from 'lunr';
import { Property } from '@/services/api';

interface SearchResult {
  ref: string;
  score: number;
  property: Property;
}

export function useLunrSearch(properties: Property[]) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Build the Lunr index when properties change
  const index = useMemo(() => {
    if (properties.length === 0) return null;

    return lunr(function () {
      this.ref('id');

      // Fields to search with boosting
      this.field('title', { boost: 10 });
      this.field('description', { boost: 5 });
      this.field('city', { boost: 8 });
      this.field('state', { boost: 6 });
      this.field('address', { boost: 4 });
      this.field('neighborhood', { boost: 4 });
      this.field('property_type', { boost: 3 });
      this.field('tags', { boost: 2 });

      // Add documents to the index
      properties.forEach((property) => {
        this.add({
          id: property.id,
          title: property.title || '',
          description: property.description || '',
          city: property.location?.city || '',
          state: property.location?.state || '',
          address: property.location?.address || '',
          neighborhood: property.location?.neighborhood || '',
          property_type: property.property_type || '',
          tags: property.tags?.join(' ') || '',
        });
      });
    });
  }, [properties]);

  // Create a map for quick property lookup
  const propertyMap = useMemo(() => {
    const map = new Map<string, Property>();
    properties.forEach((property) => {
      map.set(property.id, property);
    });
    return map;
  }, [properties]);

  // Perform search
  const performSearch = useCallback((query: string) => {
    if (!index || !query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);

    try {
      // Add wildcard for partial matching
      const searchTerms = query
        .trim()
        .split(/\s+/)
        .map((term) => `${term}*`)
        .join(' ');

      const results = index.search(searchTerms);

      const mappedResults: SearchResult[] = results
        .map((result) => {
          const property = propertyMap.get(result.ref);
          if (!property) return null;
          return {
            ref: result.ref,
            score: result.score,
            property,
          };
        })
        .filter((result): result is SearchResult => result !== null);

      setSearchResults(mappedResults);
    } catch (error) {
      // If search syntax is invalid, try a simpler search
      console.warn('Search error, trying simple search:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [index, propertyMap]);

  // Debounced search effect
  useEffect(() => {
    const timer = setTimeout(() => {
      performSearch(searchQuery);
    }, 150);

    return () => clearTimeout(timer);
  }, [searchQuery, performSearch]);

  // Get filtered properties based on search
  const filteredProperties = useMemo(() => {
    if (!searchQuery.trim()) {
      return properties;
    }
    return searchResults.map((result) => result.property);
  }, [searchQuery, searchResults, properties]);

  return {
    searchQuery,
    setSearchQuery,
    filteredProperties,
    isSearching,
    resultCount: searchQuery.trim() ? searchResults.length : properties.length,
    hasResults: searchQuery.trim() ? searchResults.length > 0 : properties.length > 0,
  };
}
