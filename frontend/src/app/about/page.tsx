export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">About Us</h1>
            
            <div className="prose max-w-none">
              <p className="text-lg text-gray-700 mb-6">
                Welcome to Real Estate, your trusted partner in finding the perfect property. With years of experience in the real estate market, we pride ourselves on providing exceptional service and helping our clients achieve their property dreams.
              </p>

              <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Our Mission</h2>
              <p className="text-gray-700 mb-6">
                Our mission is to make property buying, selling, and renting as seamless as possible. We strive to provide comprehensive property solutions while maintaining the highest standards of professionalism and integrity.
              </p>

              <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Why Choose Us?</h2>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-6">
                <li>Extensive portfolio of premium properties</li>
                <li>Professional and experienced team</li>
                <li>Personalized service for each client</li>
                <li>Transparent and ethical business practices</li>
                <li>Competitive pricing and market insights</li>
              </ul>

              <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Our Services</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Property Sales</h3>
                  <p className="text-gray-700">
                    Expert guidance throughout your property buying or selling journey.
                  </p>
                </div>
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Property Management</h3>
                  <p className="text-gray-700">
                    Comprehensive property management services for landlords and investors.
                  </p>
                </div>
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Property Consultation</h3>
                  <p className="text-gray-700">
                    Professional advice on property investment and market trends.
                  </p>
                </div>
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Property Valuation</h3>
                  <p className="text-gray-700">
                    Accurate property valuations based on market analysis.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 