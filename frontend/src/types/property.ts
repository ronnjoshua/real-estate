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

export interface PropertyCreate {
    title: string;
    description: string;
    price: number;
    property_type: string;
    location: string;
    bedrooms: number;
    bathrooms: number;
    area: number;
    images: string[];
}

export interface PropertyUpdate {
    title?: string;
    description?: string;
    price?: number;
    property_type?: string;
    location?: string;
    bedrooms?: number;
    bathrooms?: number;
    area?: number;
    status?: 'available' | 'sold' | 'pending';
    images?: string[];
} 