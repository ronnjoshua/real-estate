'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { fetchPropertyById } from '@/services/api';
import { Property } from '@/types/property';
import ImageGallery from '@/components/ImageGallery';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function PropertyDetailPage() {
  const { id } = useParams();
  const [property, setProperty] = useState<Property | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Contact form state
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    message: '',
  });
  const [contactStatus, setContactStatus] = useState({ type: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const loadProperty = async () => {
      try {
        if (typeof id !== 'string') {
          throw new Error('Invalid property ID');
        }

        const propertyData = await fetchPropertyById(id);
        setProperty(propertyData);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load property');
        setLoading(false);
      }
    };

    loadProperty();
  }, [id]);

  const handleContactSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!property) return;

    setIsSubmitting(true);
    setContactStatus({ type: '', message: '' });

    try {
      const response = await fetch(`${API_BASE_URL}/contact/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: contactForm.name,
          email: contactForm.email,
          phone: '',
          message: `Property Inquiry: ${property.title}\nAddress: ${property.location.address}, ${property.location.city}, ${property.location.state}\nPrice: $${property.price.toLocaleString()}\n\nMessage:\n${contactForm.message}`,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setContactStatus({ type: 'success', message: 'Your message has been sent! We will contact you soon.' });
        setContactForm({ name: '', email: '', message: '' });
      } else {
        setContactStatus({ type: 'error', message: data.detail || 'Failed to send message. Please try again.' });
      }
    } catch (error) {
      console.error('Error submitting contact form:', error);
      setContactStatus({ type: 'error', message: 'Failed to send message. Please try again later.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-4 text-gray-600">Loading property details...</p>
        </div>
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <div className="text-2xl text-red-600 mb-4">{error || 'Property not found'}</div>
        <Link
          href="/properties"
          className="text-blue-600 hover:text-blue-800 transition-colors"
        >
          Back to Properties
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <div className="mb-6">
          <Link
            href="/properties"
            className="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Properties
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Image Gallery */}
          <div className="relative">
            <ImageGallery
              images={property.media?.images || []}
              alt={property.title}
            />
            {/* Status Badge */}
            <div className="absolute top-4 right-4 z-30">
              <span className={`px-4 py-2 text-white text-sm font-semibold rounded-full shadow-lg ${
                property.status === 'available' ? 'bg-green-600' :
                property.status === 'pending' ? 'bg-yellow-600' :
                'bg-red-600'
              }`}>
                {property.status.charAt(0).toUpperCase() + property.status.slice(1)}
              </span>
            </div>
          </div>
          
          <div className="p-8">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{property.title}</h1>
                <p className="text-xl text-gray-600">
                  {property.location.address}, {property.location.city}, {property.location.state} {property.location.zip_code}
                </p>
              </div>
              <div className="mt-4 lg:mt-0">
                <span className="text-3xl font-bold text-blue-600">
                  ${property.price.toLocaleString()}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <span className="block text-gray-500">Bedrooms</span>
                <span className="text-xl font-semibold text-gray-900">{property.bedrooms}</span>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <span className="block text-gray-500">Bathrooms</span>
                <span className="text-xl font-semibold text-gray-900">{property.bathrooms}</span>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <span className="block text-gray-500">Area</span>
                <span className="text-xl font-semibold text-gray-900">{property.area.toLocaleString()} sqft</span>
              </div>
            </div>

            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Description</h2>
              <p className="text-gray-600 leading-relaxed">{property.description}</p>
            </div>

            <div className="border-t pt-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Contact Agent</h2>

              {contactStatus.message && (
                <div className={`p-4 rounded-md mb-6 ${
                  contactStatus.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
                }`}>
                  {contactStatus.message}
                </div>
              )}

              <form onSubmit={handleContactSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={contactForm.name}
                    onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your name"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Your Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={contactForm.email}
                    onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your email"
                    required
                  />
                </div>
                <div className="md:col-span-2">
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                    Message
                  </label>
                  <textarea
                    id="message"
                    rows={4}
                    value={contactForm.message}
                    onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="I'm interested in this property..."
                    required
                  ></textarea>
                </div>
                <div className="md:col-span-2">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {isSubmitting ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Sending...
                      </>
                    ) : (
                      'Send Message'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 