// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Debug logging
console.log('Environment variable NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('Final API_BASE_URL being used:', API_BASE_URL);

// Token storage utilities
const TOKEN_KEY = 'auth_tokens';

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

const getTokens = (): AuthTokens | null => {
  try {
    const tokens = sessionStorage.getItem(TOKEN_KEY);
    return tokens ? JSON.parse(tokens) : null;
  } catch (error) {
    console.error('Error retrieving tokens:', error);
    return null;
  }
};

const setTokens = (tokens: AuthTokens) => {
  try {
    sessionStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
  } catch (error) {
    console.error('Error storing tokens:', error);
  }
};

// Property interfaces matching backend models
export interface PropertyLocation {
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  latitude?: number;
  longitude?: number;
  neighborhood?: string;
}

export interface PropertyFeatures {
  parking_spaces?: number;
  has_garage: boolean;
  has_pool: boolean;
  has_garden: boolean;
  has_balcony: boolean;
  has_basement: boolean;
  has_attic: boolean;
  is_furnished: boolean;
  pet_friendly: boolean;
  year_built?: number;
  lot_size?: number;
  hoa_fee?: number;
  property_tax?: number;
}

export interface PropertyMedia {
  images: string[];
  virtual_tour_url?: string;
  video_url?: string;
  floor_plan_url?: string;
  documents: string[];
}

export interface Property {
  id: string;
  title: string;
  description: string;
  price: number;
  location: PropertyLocation;
  property_type: 'house' | 'apartment' | 'condo' | 'townhouse' | 'commercial' | 'land';
  bedrooms: number;
  bathrooms: number;
  area: number;
  features: PropertyFeatures;
  media: PropertyMedia;
  status: 'available' | 'sold' | 'rented' | 'pending' | 'inactive';
  agent_id?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface PropertyFilters {
  property_type?: string;
  status?: string;
  min_price?: number;
  max_price?: number;
  min_bedrooms?: number;
  max_bedrooms?: number;
  min_bathrooms?: number;
  max_bathrooms?: number;
  min_area?: number;
  max_area?: number;
  city?: string;
  state?: string;
  zip_code?: string;
  has_garage?: boolean;
  has_pool?: boolean;
  has_garden?: boolean;
  pet_friendly?: boolean;
  year_built_min?: number;
  year_built_max?: number;
}

export interface PropertyResponse {
  properties: Property[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

// API client with automatic token refresh
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async refreshTokens(): Promise<boolean> {
    try {
      const tokens = getTokens();
      if (!tokens?.refresh_token) {
        return false;
      }

      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh_token: tokens.refresh_token,
        }),
      });

      if (!response.ok) {
        return false;
      }

      const newTokens: AuthTokens = await response.json();
      setTokens(newTokens);
      return true;
    } catch (error) {
      console.error('Error refreshing tokens:', error);
      return false;
    }
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    requireAuth = false
  ): Promise<T> {
    let tokens = getTokens();

    // Add authorization header if tokens are available
    if (tokens && requireAuth) {
      options.headers = {
        ...options.headers,
        Authorization: `Bearer ${tokens.access_token}`,
      };
    }

    const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
    console.log('Making request to URL:', url);
    console.log('this.baseURL:', this.baseURL);
    console.log('endpoint:', endpoint);
    let response = await fetch(url, options);

    // If unauthorized and we have tokens, try to refresh
    if (response.status === 401 && tokens && requireAuth) {
      const refreshSuccess = await this.refreshTokens();
      if (refreshSuccess) {
        tokens = getTokens();
        if (tokens) {
          options.headers = {
            ...options.headers,
            Authorization: `Bearer ${tokens.access_token}`,
          };
          response = await fetch(url, options);
        }
      }
    }

    return this.handleResponse<T>(response);
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ 
        detail: `HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(error.detail || error.message || 'An error occurred');
    }
    
    // Handle empty responses
    if (response.status === 204) {
      return {} as T;
    }
    
    return response.json();
  }

  // Properties API methods
  async getProperties(params: {
    skip?: number;
    limit?: number;
    filters?: PropertyFilters;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  } = {}): Promise<PropertyResponse> {
    const queryParams = new URLSearchParams();
    
    if (params.skip !== undefined) queryParams.set('skip', params.skip.toString());
    if (params.limit !== undefined) queryParams.set('limit', params.limit.toString());
    if (params.sort_by) queryParams.set('sort_by', params.sort_by);
    if (params.sort_order) queryParams.set('sort_order', params.sort_order);
    
    // Add filter parameters
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.set(key, value.toString());
        }
      });
    }

    const queryString = queryParams.toString();
    const endpoint = `/properties${queryString ? `?${queryString}` : ''}`;
    
    return this.makeRequest<PropertyResponse>(endpoint);
  }

  async searchProperties(query: string, params: { skip?: number; limit?: number } = {}): Promise<PropertyResponse> {
    const queryParams = new URLSearchParams({ q: query });
    if (params.skip !== undefined) queryParams.set('skip', params.skip.toString());
    if (params.limit !== undefined) queryParams.set('limit', params.limit.toString());
    
    return this.makeRequest<PropertyResponse>(`/properties/search?${queryParams.toString()}`);
  }

  async getProperty(id: string): Promise<Property> {
    return this.makeRequest<Property>(`/properties/${id}`);
  }

  async createProperty(property: Omit<Property, 'id' | 'created_at' | 'updated_at'>): Promise<Property> {
    return this.makeRequest<Property>('/properties', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(property),
    }, true);
  }

  async updateProperty(id: string, property: Partial<Property>): Promise<Property> {
    return this.makeRequest<Property>(`/properties/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(property),
    }, true);
  }

  async deleteProperty(id: string): Promise<void> {
    return this.makeRequest<void>(`/properties/${id}`, {
      method: 'DELETE',
    }, true);
  }

  async getPropertyStats(): Promise<Record<string, unknown>> {
    return this.makeRequest<Record<string, unknown>>('/properties/admin/stats', {}, true);
  }
}

// Create and export API client instance
export const apiClient = new ApiClient(API_BASE_URL);

// Legacy function exports for backward compatibility
export async function fetchProperties(): Promise<Property[]> {
  const response = await apiClient.getProperties();
  return response.properties;
}

export async function fetchPropertyById(id: string): Promise<Property> {
  return apiClient.getProperty(id);
}

export async function createProperty(property: Omit<Property, 'id' | 'created_at' | 'updated_at'>): Promise<Property> {
  return apiClient.createProperty(property);
}

export async function updateProperty(id: string, property: Partial<Property>): Promise<Property> {
  return apiClient.updateProperty(id, property);
}

export async function deleteProperty(id: string): Promise<void> {
  return apiClient.deleteProperty(id);
}

export async function searchProperties(query: string): Promise<Property[]> {
  const response = await apiClient.searchProperties(query);
  return response.properties;
} 