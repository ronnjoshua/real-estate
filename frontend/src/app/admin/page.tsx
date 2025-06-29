'use client';

import { useState, useEffect } from 'react';
import AdminProtectedRoute from '@/components/AdminProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { UserRole } from '@/types/user';
import Image from 'next/image';
import { apiClient, Property } from '@/services/api';

const PLACEHOLDER_IMAGE = 'https://images.unsplash.com/photo-1582407947304-fd86f028f716?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80';

const isValidUrl = (url: string) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export default function AdminPage() {
  const { user, isAdmin, logout } = useAuth();
  const router = useRouter();
  const [properties, setProperties] = useState<Property[]>([]);
  const [invitations, setInvitations] = useState([]);
  const [newInvitation, setNewInvitation] = useState({
    email: '',
    role: UserRole.CLIENT,
  });
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showPropertyForm, setShowPropertyForm] = useState(false);
  
  // Form state for creating/editing properties
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: 0,
    address: '',
    city: '',
    state: '',
    zip_code: '',
    country: 'USA',
    property_type: 'house' as const,
    bedrooms: 0,
    bathrooms: 0,
    area: 0,
    status: 'available' as const,
    images: [] as string[]
  });

  useEffect(() => {
    if (!isAdmin) {
      router.push('/login');
    }
    fetchProperties();
  }, [isAdmin, router]);

  const fetchProperties = async () => {
    try {
      const result = await apiClient.getProperties({ limit: 100 });
      setProperties(result.properties);
    } catch (error) {
      console.error('Error fetching properties:', error);
    }
  };

  const handleCreateInvitation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/invite', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${user?.token}`,
        },
        body: JSON.stringify(newInvitation),
      });

      if (!response.ok) {
        throw new Error('Failed to create invitation');
      }

      const data = await response.json();
      setInvitations([...invitations, data]);
      setNewInvitation({ email: '', role: UserRole.CLIENT });
    } catch (error) {
      console.error('Error creating invitation:', error);
    }
  };

  const resetForm = () => {
    setFormData({
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
    });
  };

  const handlePropertySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const propertyData = {
        title: formData.title,
        description: formData.description,
        price: formData.price,
        location: {
          address: formData.address,
          city: formData.city,
          state: formData.state,
          zip_code: formData.zip_code,
          country: formData.country
        },
        property_type: formData.property_type,
        bedrooms: formData.bedrooms,
        bathrooms: formData.bathrooms,
        area: formData.area,
        features: {
          has_garage: false,
          has_pool: false,
          has_garden: false,
          has_balcony: false,
          has_basement: false,
          has_attic: false,
          is_furnished: false,
          pet_friendly: false
        },
        media: {
          images: formData.images.filter(url => isValidUrl(url)),
          documents: []
        },
        status: formData.status,
        agent_id: '',
        tags: []
      };

      if (isEditing && selectedProperty) {
        await apiClient.updateProperty(selectedProperty.id, propertyData);
      } else {
        await apiClient.createProperty(propertyData);
      }
      
      await fetchProperties();
      setShowPropertyForm(false);
      setSelectedProperty(null);
      resetForm();
      setIsEditing(false);
    } catch (error) {
      console.error('Error saving property:', error);
    }
  };

  const handleDeleteProperty = async (id: string) => {
    if (!confirm('Are you sure you want to delete this property?')) return;

    try {
      await apiClient.deleteProperty(id);
      await fetchProperties();
    } catch (error) {
      console.error('Error deleting property:', error);
    }
  };

  const handleEditProperty = (property: Property) => {
    setSelectedProperty(property);
    setFormData({
      title: property.title,
      description: property.description,
      price: property.price,
      address: property.location.address,
      city: property.location.city,
      state: property.location.state,
      zip_code: property.location.zip_code,
      country: property.location.country,
      property_type: property.property_type,
      bedrooms: property.bedrooms,
      bathrooms: property.bathrooms,
      area: property.area,
      status: property.status,
      images: property.media.images
    });
    setIsEditing(true);
    setShowPropertyForm(true);
  };

  return (
    <AdminProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold text-gray-900">Admin Dashboard</h1>
                </div>
              </div>
              <div className="flex items-center">
                <button
                  onClick={logout}
                  className="ml-4 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Properties Management Section */}
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-medium text-gray-900">Properties Management</h2>
                <button
                  onClick={() => {
                    setShowPropertyForm(true);
                    setIsEditing(false);
                    setSelectedProperty(null);
                    resetForm();
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Add New Property
                </button>
              </div>

              {showPropertyForm && (
                <div className="mb-8 bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    {isEditing ? 'Edit Property' : 'Add New Property'}
                  </h3>
                  <form onSubmit={handlePropertySubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Title</label>
                        <input
                          type="text"
                          value={formData.title}
                          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">City</label>
                        <input
                          type="text"
                          value={formData.city}
                          onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">State</label>
                        <input
                          type="text"
                          value={formData.state}
                          onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Price</label>
                        <input
                          type="number"
                          value={formData.price}
                          onChange={(e) => setFormData({ ...formData, price: Number(e.target.value) })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Property Type</label>
                        <select
                          value={formData.property_type}
                          onChange={(e) => setFormData({ ...formData, property_type: e.target.value as any })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
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
                          onChange={(e) => setFormData({ ...formData, bedrooms: Number(e.target.value) })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Bathrooms</label>
                        <input
                          type="number"
                          value={formData.bathrooms}
                          onChange={(e) => setFormData({ ...formData, bathrooms: Number(e.target.value) })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Area (sqft)</label>
                        <input
                          type="number"
                          value={formData.area}
                          onChange={(e) => setFormData({ ...formData, area: Number(e.target.value) })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Status</label>
                        <select
                          value={formData.status}
                          onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
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
                        onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Description</label>
                      <textarea
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        rows={4}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Image URLs (one per line)</label>
                      <textarea
                        value={formData.images.join('\n')}
                        onChange={(e) => {
                          const urls = e.target.value.split('\n').filter(url => url.trim());
                          setFormData({ ...formData, images: urls });
                        }}
                        rows={3}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="https://example.com/image1.jpg&#10;https://example.com/image2.jpg"
                      />
                    </div>
                    <div className="flex justify-end space-x-3">
                      <button
                        type="button"
                        onClick={() => {
                          setShowPropertyForm(false);
                          setSelectedProperty(null);
                          setIsEditing(false);
                          resetForm();
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        {isEditing ? 'Update Property' : 'Create Property'}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Image</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {properties.map((property) => (
                      <tr key={property.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="relative h-16 w-16">
                            <Image
                              src={property.media.images && property.media.images.length > 0 && isValidUrl(property.media.images[0])
                                ? property.media.images[0]
                                : PLACEHOLDER_IMAGE}
                              alt={property.title}
                              fill
                              style={{ objectFit: 'cover' }}
                              className="rounded-md"
                            />
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{property.title}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-500">{property.location.city}, {property.location.state}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">${property.price.toLocaleString()}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            property.status === 'available' ? 'bg-green-100 text-green-800' :
                            property.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {property.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-3">
                          <button
                            onClick={() => handleEditProperty(property)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteProperty(property.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Invitations Section */}
            <div className="mt-8 bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Active Invitations</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                        Role
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {invitations.map((invitation: any) => (
                      <tr key={invitation.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {invitation.email}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {invitation.role}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`px-2 py-1 rounded-full ${
                            invitation.is_used 
                              ? 'bg-gray-100 text-gray-800' 
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {invitation.is_used ? 'Used' : 'Active'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </AdminProtectedRoute>
  );
}