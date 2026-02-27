'use client';

import { useState, useCallback, memo } from 'react';
// CloudinaryUpload temporarily disabled for debugging
// import CloudinaryUpload from './CloudinaryUpload';

interface PropertyFormData {
  title: string;
  description: string;
  price: number;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  property_type: 'house' | 'apartment' | 'condo' | 'townhouse' | 'commercial' | 'land';
  bedrooms: number;
  bathrooms: number;
  area: number;
  status: 'available' | 'sold' | 'rented' | 'pending' | 'inactive';
  images: string[];
}

interface PropertyFormProps {
  initialData?: PropertyFormData;
  isEditing: boolean;
  onSubmit: (data: PropertyFormData) => Promise<void>;
  onCancel: () => void;
}

const defaultFormData: PropertyFormData = {
  title: '',
  description: '',
  price: 0,
  address: '',
  city: '',
  state: '',
  zip_code: '',
  country: 'USA',
  property_type: 'house',
  bedrooms: 0,
  bathrooms: 0,
  area: 0,
  status: 'available',
  images: []
};

function PropertyForm({ initialData, isEditing, onSubmit, onCancel }: PropertyFormProps) {
  const [formData, setFormData] = useState<PropertyFormData>(initialData || defaultFormData);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = useCallback((field: keyof PropertyFormData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleImagesChange = useCallback((newImages: string[]) => {
    setFormData(prev => ({ ...prev, images: newImages }));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mb-8 bg-gray-50 p-6 rounded-lg">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        {isEditing ? 'Edit Property' : 'Add New Property'}
      </h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">City</label>
            <input
              type="text"
              value={formData.city}
              onChange={(e) => handleChange('city', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">State</label>
            <input
              type="text"
              value={formData.state}
              onChange={(e) => handleChange('state', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Price</label>
            <input
              type="number"
              value={formData.price}
              onChange={(e) => handleChange('price', Number(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Property Type</label>
            <select
              value={formData.property_type}
              onChange={(e) => handleChange('property_type', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              required
            >
              <option value="house">House</option>
              <option value="apartment">Apartment</option>
              <option value="condo">Condo</option>
              <option value="townhouse">Townhouse</option>
              <option value="commercial">Commercial</option>
              <option value="land">Land</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Bedrooms</label>
            <input
              type="number"
              value={formData.bedrooms}
              onChange={(e) => handleChange('bedrooms', Number(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Bathrooms</label>
            <input
              type="number"
              value={formData.bathrooms}
              onChange={(e) => handleChange('bathrooms', Number(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Area (sqft)</label>
            <input
              type="number"
              value={formData.area}
              onChange={(e) => handleChange('area', Number(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Status</label>
            <select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              required
            >
              <option value="available">Available</option>
              <option value="pending">Pending</option>
              <option value="sold">Sold</option>
              <option value="rented">Rented</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Address</label>
          <input
            type="text"
            value={formData.address}
            onChange={(e) => handleChange('address', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={4}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
            required
          />
        </div>
        {/* Simple image URL input - Cloudinary disabled for debugging */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Image URLs (one per line)</label>
          <textarea
            value={formData.images.join('\n')}
            onChange={(e) => {
              const urls = e.target.value.split('\n').filter(url => url.trim());
              handleImagesChange(urls);
            }}
            rows={3}
            placeholder="https://example.com/image1.jpg&#10;https://example.com/image2.jpg"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
          />
          <p className="text-xs text-gray-500 mt-1">Enter image URLs, one per line</p>
        </div>
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-400"
          >
            {isSubmitting ? 'Saving...' : (isEditing ? 'Update Property' : 'Create Property')}
          </button>
        </div>
      </form>
    </div>
  );
}

export default memo(PropertyForm);
