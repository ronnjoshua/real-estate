// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Interface for Property
export interface Property {
  id: string;
  title: string;
  description: string;
  price: number;
  location: string;
  bedrooms: number;
  bathrooms: number;
  area: number;
  images: string[];
  property_type: string;
  status: 'available' | 'sold' | 'pending';
  created_at?: string;
  updated_at?: string;
}

// Helper function to handle API responses
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'An error occurred' }));
    throw new Error(error.message || 'An error occurred');
  }
  return response.json();
}

// Function to fetch all properties
export async function fetchProperties(): Promise<Property[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/properties`);
    return handleResponse<Property[]>(response);
  } catch (error) {
    console.error('Error fetching properties:', error);
    throw error;
  }
}

// Function to fetch a single property by ID
export async function fetchPropertyById(id: string): Promise<Property> {
  try {
    const response = await fetch(`${API_BASE_URL}/properties/${id}`);
    return handleResponse<Property>(response);
  } catch (error) {
    console.error('Error fetching property:', error);
    throw error;
  }
}

// Function to create a new property
export async function createProperty(property: Omit<Property, 'id'>): Promise<Property> {
  try {
    const response = await fetch(`${API_BASE_URL}/properties`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(property),
    });
    return handleResponse<Property>(response);
  } catch (error) {
    console.error('Error creating property:', error);
    throw error;
  }
}

// Function to update a property
export async function updateProperty(id: string, property: Partial<Property>): Promise<Property> {
  try {
    const response = await fetch(`${API_BASE_URL}/properties/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(property),
    });
    return handleResponse<Property>(response);
  } catch (error) {
    console.error('Error updating property:', error);
    throw error;
  }
}

// Function to delete a property
export async function deleteProperty(id: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/properties/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(response);
  } catch (error) {
    console.error('Error deleting property:', error);
    throw error;
  }
}

// Function to search properties
export async function searchProperties(query: string): Promise<Property[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/properties/search?q=${encodeURIComponent(query)}`);
    return handleResponse<Property[]>(response);
  } catch (error) {
    console.error('Error searching properties:', error);
    throw error;
  }
} 