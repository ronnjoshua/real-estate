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
    bedrooms: number;
    bathrooms: number;
    area: number;
    property_type: 'house' | 'apartment' | 'condo' | 'townhouse' | 'commercial' | 'land';
    features: PropertyFeatures;
    media: PropertyMedia;
    status: 'available' | 'sold' | 'rented' | 'pending' | 'inactive';
    agent_id?: string;
    tags: string[];
    created_at: string;
    updated_at: string;
}

export interface PropertyCreate {
    title: string;
    description: string;
    price: number;
    property_type: 'house' | 'apartment' | 'condo' | 'townhouse' | 'commercial' | 'land';
    location: PropertyLocation;
    bedrooms: number;
    bathrooms: number;
    area: number;
    features: PropertyFeatures;
    media: PropertyMedia;
    status: 'available' | 'sold' | 'rented' | 'pending' | 'inactive';
    agent_id?: string;
    tags: string[];
}

export interface PropertyUpdate {
    title?: string;
    description?: string;
    price?: number;
    property_type?: 'house' | 'apartment' | 'condo' | 'townhouse' | 'commercial' | 'land';
    location?: PropertyLocation;
    bedrooms?: number;
    bathrooms?: number;
    area?: number;
    features?: PropertyFeatures;
    media?: PropertyMedia;
    status?: 'available' | 'sold' | 'rented' | 'pending' | 'inactive';
    agent_id?: string;
    tags?: string[];
} 