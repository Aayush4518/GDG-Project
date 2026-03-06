/**
 * Simple test script to verify API service functionality
 * Run with: node test-api.js
 */

import apiService from './src/services/apiService.js';

async function testAPI() {
  console.log('🧪 Testing Dashboard API Service...\n');

  try {
    // Test 1: Connection test
    console.log('1. Testing backend connection...');
    const isConnected = await apiService.testConnection();
    console.log(`   ✅ Backend connection: ${isConnected ? 'SUCCESS' : 'FAILED'}\n`);

    if (isConnected) {
      // Test 2: Get active tourists
      console.log('2. Fetching active tourists...');
      const tourists = await apiService.getActiveTourists();
      console.log(`   ✅ Active tourists: ${tourists.length} found`);
      if (tourists.length > 0) {
        console.log(`   📍 Sample tourist: ${JSON.stringify(tourists[0], null, 2)}\n`);
      }

      // Test 3: Get analytics
      console.log('3. Fetching analytics...');
      const analytics = await apiService.getAnalytics();
      console.log(`   ✅ Analytics: ${JSON.stringify(analytics, null, 2)}\n`);

      // Test 4: Get risk zones
      console.log('4. Fetching risk zones...');
      const riskZones = await apiService.getRiskZones();
      console.log(`   ✅ Risk zones: ${riskZones.length} found\n`);

      // Test 5: Test ledger verification
      console.log('5. Testing ledger verification...');
      const ledgerResult = await apiService.verifyLedger();
      console.log(`   ✅ Ledger verification: ${JSON.stringify(ledgerResult, null, 2)}\n`);

      console.log('🎉 All API tests completed successfully!');
    } else {
      console.log('❌ Backend not available. Make sure the backend server is running on localhost:8000');
    }

  } catch (error) {
    console.error('❌ API test failed:', error.message);
    console.log('\n💡 Make sure:');
    console.log('   - Backend server is running on localhost:8000');
    console.log('   - All required endpoints are implemented');
    console.log('   - CORS is properly configured');
  }
}

testAPI();
