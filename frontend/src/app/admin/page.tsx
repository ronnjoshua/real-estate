'use client';

import { useState, useEffect } from 'react';
import AdminProtectedRoute from '@/components/AdminProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { UserRole } from '@/types/user';
import Image from 'next/image';
import { firestoreService } from '@/services/firebase';
import { Property } from '@/types/property';

interface Property {
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
  status: 'active' | 'pending' | 'sold';
}

const initialPropertyState: Property = {
  id: '',
  title: '',
  description: '',
  price: 0,
  location: '',
  bedrooms: 0,
  bathrooms: 0,
  area: 0,
  images: [],
  property_type: '',
  status: 'active'
};

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
  const [newProperty, setNewProperty] = useState<Property>(initialPropertyState);
  const [showPropertyForm, setShowPropertyForm] = useState(false);

  useEffect(() => {
    if (!isAdmin) {
      router.push('/login');
    }
    fetchProperties();
  }, [isAdmin, router]);

  const fetchProperties = async () => {
    try {
      const result = await firestoreService.getProperties(100); // Fetch up to 100 properties
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

  const handlePropertySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Validate image URLs before saving
      let validatedImages: string[] = [];
      if (isEditing && selectedProperty) {
        validatedImages = selectedProperty.images.filter(url => isValidUrl(url));
        const updated = await firestoreService.updateProperty(selectedProperty.id, {
          ...selectedProperty,
          images: validatedImages
        });
        if (updated) {
          await fetchProperties();
        }
      } else {
        validatedImages = newProperty.images.filter(url => isValidUrl(url));
        const created = await firestoreService.createProperty({
          ...newProperty,
          images: validatedImages
        });
        if (created) {
          await fetchProperties();
        }
      }
      setShowPropertyForm(false);
      setSelectedProperty(null);
      setNewProperty(initialPropertyState);
      setIsEditing(false);
    } catch (error) {
      console.error('Error saving property:', error);
    }
  };

  const handleDeleteProperty = async (id: string) => {
    if (!confirm('Are you sure you want to delete this property?')) return;

    try {
      const success = await firestoreService.deleteProperty(id);
      if (success) {
        await fetchProperties();
      }
    } catch (error) {
      console.error('Error deleting property:', error);
    }
  };

  const handleEditProperty = (property: Property) => {
    setSelectedProperty(property);
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
                    setNewProperty(initialPropertyState);
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
                          value={isEditing ? selectedProperty?.title : newProperty.title}
                          onChange={(e) => isEditing 
                            ? setSelectedProperty({ ...selectedProperty!, title: e.target.value })
                            : setNewProperty({ ...newProperty, title: e.target.value })
                          }
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Location</label>
                        <input
                          type="text"
                          value={isEditing ? selectedProperty?.location : newProperty.location}
                          onChange={(e) => isEditing
                            ? setSelectedProperty({ ...selectedProperty!, location: e.target.value })
                            : setNewProperty({ ...newProperty, location: e.target.value })
                          }
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Price</label>
                        <input
                          type="number"
                          value={isEditing ? selectedProperty?.price : newProperty.price}
                          onChange={(e) => isEditing
                            ? setSelectedProperty({ ...selectedProperty!, price: Number(e.target.value) })
                            : setNewProperty({ ...newProperty, price: Number(e.target.value) })
                          }
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Property Type</label>
                        <input
                          type="text"
                          value={isEditing ? selectedProperty?.property_type : newProperty.property_type}
                          onChange={(e) => isEditing
                            ? setSelectedProperty({ ...selectedProperty!, property_type: e.target.value })
                            : setNewProperty({ ...newProperty, property_type: e.target.value })
                          }
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Bedrooms</label>
                        <input
                          type="number"
                          value={isEditing ? selectedProperty?.bedrooms : newProperty.bedrooms}
                          onChange={(e) => isEditing
                            ? setSelectedProperty({ ...selectedProperty!, bedrooms: Number(e.target.value) })
                            : setNewProperty({ ...newProperty, bedrooms: Number(e.target.value) })
                          }
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Bathrooms</label>
                        <input
                          type="number"
                          value={isEditing ? selectedProperty?.bathrooms : newProperty.bathrooms}
                          onChange={(e) => isEditing
                            ? setSelectedProperty({ ...selectedProperty!, bathrooms: Number(e.target.value) })
                            : setNewProperty({ ...newProperty, bathrooms: Number(e.target.value) })
                          }
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Area (sqft)</label>
                        <input
                          type="number"
                          value={isEditing ? selectedProperty?.area : newProperty.area}
                          onChange={(e) => isEditing
                            ? setSelectedProperty({ ...selectedProperty!, area: Number(e.target.value) })
                            : setNewProperty({ ...newProperty, area: Number(e.target.value) })
                          }
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Status</label>
                        <select
                          value={isEditing ? selectedProperty?.status : newProperty.status}
                          onChange={(e) => isEditing
                            ? setSelectedProperty({ ...selectedProperty!, status: e.target.value as 'active' | 'pending' | 'sold' })
                            : setNewProperty({ ...newProperty, status: e.target.value as 'active' | 'pending' | 'sold' })
                          }
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          required
                        >
                          <option value="active">Active</option>
                          <option value="pending">Pending</option>
                          <option value="sold">Sold</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Description</label>
                      <textarea
                        value={isEditing ? selectedProperty?.description : newProperty.description}
                        onChange={(e) => isEditing
                          ? setSelectedProperty({ ...selectedProperty!, description: e.target.value })
                          : setNewProperty({ ...newProperty, description: e.target.value })
                        }
                        rows={4}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Image URLs (one per line)</label>
                      <textarea
                        value={isEditing ? selectedProperty?.images.join('\n') : newProperty.images.join('\n')}
                        onChange={(e) => {
                          const urls = e.target.value.split('\n').filter(url => url.trim());
                          isEditing
                            ? setSelectedProperty({ ...selectedProperty!, images: urls })
                            : setNewProperty({ ...newProperty, images: urls });
                        }}
                        rows={3}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="https://example.com/image1.jpg&#10;https://example.com/image2.jpg"
                        required
                      />
                    </div>
                    <div className="flex justify-end space-x-3">
                      <button
                        type="button"
                        onClick={() => {
                          setShowPropertyForm(false);
                          setSelectedProperty(null);
                          setIsEditing(false);
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
                          <div className="relative h-60">
                            <Image
                              src={property.images && property.images.length > 0 && isValidUrl(property.images[0])
                                ? property.images[0]
                                : PLACEHOLDER_IMAGE}
                              alt={property.title}
                              fill
                              style={{ objectFit: 'cover' }}
                              className="rounded-t-lg"
                            />
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{property.title}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-500">{property.location}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">${property.price.toLocaleString()}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            property.status === 'active' ? 'bg-green-100 text-green-800' :
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