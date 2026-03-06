#!/usr/bin/env node

/**
 * Test script to verify API integration between mobile app and backend
 * This simulates the mobile app's API calls to ensure they work correctly
 */

const API_BASE = 'http://localhost:8000/api/v1';

async function testAPI() {
  console.log('🧪 Testing API Integration...\n');

  try {
    // Test 1: Registration
    console.log('1️⃣ Testing Registration API...');
    const registrationData = {
      name: 'Mobile App Test User',
      kyc_hash: 'mobile_test_kyc_456',
      emergency_contact: {
        name: 'Emergency Contact',
        phone: '+91-9876543210',
        relation: 'Family'
      },
      trip_end_date: new Date('2024-12-31T23:59:59Z').toISOString()
    };

    const registerResponse = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registrationData)
    });

    if (!registerResponse.ok) {
      throw new Error(`Registration failed: ${registerResponse.status} ${registerResponse.statusText}`);
    }

    const registerResult = await registerResponse.json();
    console.log('✅ Registration successful:', registerResult.tourist_id);

    const touristId = registerResult.tourist_id;

    // Test 2: Location Tracking
    console.log('\n2️⃣ Testing Location Tracking API...');
    const locationData = {
      latitude: 28.6139,
      longitude: 77.2090,
      timestamp: new Date().toISOString()
    };

    const locationResponse = await fetch(`${API_BASE}/tourists/${touristId}/location`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locationData)
    });

    if (!locationResponse.ok) {
      throw new Error(`Location tracking failed: ${locationResponse.status} ${locationResponse.statusText}`);
    }

    const locationResult = await locationResponse.json();
    console.log('✅ Location tracking successful:', locationResult.message);

    // Test 3: Panic Button
    console.log('\n3️⃣ Testing Panic Button API...');
    const panicData = {
      latitude: 28.6139,
      longitude: 77.2090,
      timestamp: new Date().toISOString(),
      message: 'Emergency test from mobile app'
    };

    const panicResponse = await fetch(`${API_BASE}/tourists/${touristId}/panic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(panicData)
    });

    if (!panicResponse.ok) {
      throw new Error(`Panic button failed: ${panicResponse.status} ${panicResponse.statusText}`);
    }

    const panicResult = await panicResponse.json();
    console.log('✅ Panic button successful:', panicResult.message);

    // Test 4: Check Active Tourists
    console.log('\n4️⃣ Testing Active Tourists API...');
    const activeTouristsResponse = await fetch(`${API_BASE}/dashboard/active-tourists`);
    
    if (!activeTouristsResponse.ok) {
      throw new Error(`Active tourists failed: ${activeTouristsResponse.status} ${activeTouristsResponse.statusText}`);
    }

    const activeTourists = await activeTouristsResponse.json();
    console.log('✅ Active tourists retrieved:', activeTourists.length, 'tourists');
    
    // Find our test user
    const testUser = activeTourists.find(t => t.tourist_id === touristId);
    if (testUser) {
      console.log('✅ Test user found in active tourists:', testUser.name);
      if (testUser.last_known_location) {
        console.log('✅ Test user has location data:', testUser.last_known_location);
      }
    }

    console.log('\n🎉 All API tests passed! Mobile app integration is working correctly.');
    console.log('\n📱 Next steps:');
    console.log('1. Start an Android emulator or connect a physical device');
    console.log('2. Run: npm run android');
    console.log('3. Register a new user in the mobile app');
    console.log('4. Check the web dashboard at http://localhost:5173');

  } catch (error) {
    console.error('❌ API test failed:', error.message);
    process.exit(1);
  }
}

// Run the test
testAPI();
