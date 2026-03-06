// Script to generate and save 500+ dummy data entries
// Run with: node generate-dummy-data.js

import fs from 'fs';
import path from 'path';

// Comprehensive Dummy Data Generator
const generateDummyData = () => {
  const firstNames = [
    "Aarav", "Priya", "Vikram", "Anita", "Rajesh", "Sneha", "Arjun", "Kavya", "Rohit", "Divya",
    "Emma", "James", "Sarah", "David", "Lisa", "Michael", "Jennifer", "Robert", "Maria", "John",
    "Pierre", "Marie", "Jean", "Sophie", "Antoine", "Camille", "Nicolas", "Isabelle", "François", "Claire",
    "Hans", "Greta", "Klaus", "Ingrid", "Werner", "Ursula", "Friedrich", "Brunhilde", "Otto", "Helga",
    "Hiroshi", "Yuki", "Takeshi", "Akiko", "Kenji", "Mayumi", "Satoshi", "Naomi", "Daisuke", "Emi",
    "Zhang", "Li", "Wang", "Liu", "Chen", "Yang", "Zhao", "Huang", "Wu", "Zhou",
    "Ahmed", "Fatima", "Ali", "Aisha", "Omar", "Zara", "Hassan", "Nadia", "Khalid", "Layla",
    "Carlos", "Isabella", "Diego", "Sofia", "Fernando", "Valentina", "Ricardo", "Camila", "Eduardo", "Lucia"
  ];

  const lastNames = [
    "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Verma", "Yadav", "Reddy", "Nair", "Iyer",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Dubois", "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Leroy", "Moreau",
    "Mueller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann",
    "Tanaka", "Suzuki", "Takahashi", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato", "Yoshida",
    "Zhang", "Wang", "Li", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou",
    "Al-Ahmad", "Al-Hassan", "Al-Mahmoud", "Al-Rashid", "Al-Zahra", "Al-Nasser", "Al-Khalil", "Al-Sabah", "Al-Mansour", "Al-Farisi",
    "Lopez", "Gonzalez", "Rodriguez", "Sanchez", "Ramirez", "Cruz", "Flores", "Gutierrez", "Morales", "Ortiz"
  ];

  const nationalities = [
    "Indian", "American", "British", "French", "German", "Japanese", "Chinese", "Spanish", "Italian", "Australian",
    "Canadian", "Russian", "Brazilian", "Mexican", "Dutch", "Swiss", "Belgian", "Swedish", "Norwegian", "Danish",
    "South Korean", "Thai", "Malaysian", "Singaporean", "Indonesian", "Vietnamese", "Philippine", "Bangladeshi", "Sri Lankan", "Nepalese"
  ];

  const countryPhoneCodes = {
    "Indian": "+91", "American": "+1", "British": "+44", "French": "+33", "German": "+49",
    "Japanese": "+81", "Chinese": "+86", "Spanish": "+34", "Italian": "+39", "Australian": "+61",
    "Canadian": "+1", "Russian": "+7", "Brazilian": "+55", "Mexican": "+52", "Dutch": "+31",
    "Swiss": "+41", "Belgian": "+32", "Swedish": "+46", "Norwegian": "+47", "Danish": "+45",
    "South Korean": "+82", "Thai": "+66", "Malaysian": "+60", "Singaporean": "+65", "Indonesian": "+62",
    "Vietnamese": "+84", "Philippine": "+63", "Bangladeshi": "+880", "Sri Lankan": "+94", "Nepalese": "+977"
  };

  const neLocations = [
    { name: "Shillong Peak", lat: 25.5941, lng: 91.8825, district: "East Khasi Hills" },
    { name: "Cherrapunji", lat: 25.4670, lng: 91.3662, district: "East Khasi Hills" },
    { name: "Kaziranga National Park", lat: 26.7509, lng: 94.2037, district: "Golaghat" },
    { name: "Majuli Island", lat: 26.9510, lng: 94.2037, district: "Majuli" },
    { name: "Nathula Pass", lat: 27.0844, lng: 88.2646, district: "Gangtok" },
    { name: "Tawang Monastery", lat: 27.1024, lng: 93.6127, district: "Tawang" },
    { name: "Loktak Lake", lat: 24.7628, lng: 93.9229, district: "Bishnupur" },
    { name: "Dzukou Valley", lat: 25.1594, lng: 94.9099, district: "Kohima" },
    { name: "Kamakhya Temple", lat: 26.1445, lng: 91.7362, district: "Kamrup" },
    { name: "Umiam Lake", lat: 25.5788, lng: 91.8933, district: "Ri Bhoi" },
    { name: "Dawki River", lat: 25.1261, lng: 91.7680, district: "West Jaintia Hills" },
    { name: "Mawlynnong Village", lat: 25.2031, lng: 91.8933, district: "East Khasi Hills" },
    { name: "Aizawl", lat: 23.7307, lng: 92.7173, district: "Aizawl" },
    { name: "Kohima War Cemetery", lat: 25.6701, lng: 94.1077, district: "Kohima" },
    { name: "Tsomgo Lake", lat: 27.0844, lng: 88.2646, district: "Gangtok" },
    { name: "Bomdila", lat: 27.2615, lng: 92.4127, district: "West Kameng" },
    { name: "Ziro Valley", lat: 27.5900, lng: 93.8310, district: "Lower Subansiri" },
    { name: "Pasighat", lat: 28.0700, lng: 95.3300, district: "East Siang" },
    { name: "Lunglei", lat: 22.8900, lng: 92.7343, district: "Lunglei" },
    { name: "Jorhat", lat: 26.7509, lng: 94.2037, district: "Jorhat" },
    { name: "Sivasagar", lat: 26.9842, lng: 94.6378, district: "Sivasagar" },
    { name: "Haflong", lat: 25.1670, lng: 93.0171, district: "Dima Hasao" },
    { name: "Agartala", lat: 23.8315, lng: 91.2868, district: "West Tripura" },
    { name: "Dimapur", lat: 25.9044, lng: 93.7267, district: "Dimapur" },
    { name: "Mokokchung", lat: 26.3220, lng: 94.5228, district: "Mokokchung" },
    { name: "Tura", lat: 25.5138, lng: 90.2029, district: "West Garo Hills" },
    { name: "Along", lat: 28.1700, lng: 94.7667, district: "West Siang" },
    { name: "Bhalukpong", lat: 27.0070, lng: 92.6370, district: "West Kameng" },
    { name: "Namchi", lat: 27.1644, lng: 88.3640, district: "South Sikkim" },
    { name: "Pelling", lat: 27.3166, lng: 88.2126, district: "West Sikkim" },
    { name: "Itanagar", lat: 27.0844, lng: 93.6053, district: "Papum Pare" },
    { name: "Mon", lat: 26.7150, lng: 95.0500, district: "Mon" },
    { name: "Tuensang", lat: 26.2833, lng: 94.8333, district: "Tuensang" },
    { name: "Wokha", lat: 26.0952, lng: 94.2618, district: "Wokha" },
    { name: "Phek", lat: 25.6701, lng: 94.4501, district: "Phek" },
    { name: "Kiphire", lat: 25.8833, lng: 94.8333, district: "Kiphire" },
    { name: "Longleng", lat: 26.4333, lng: 94.8333, district: "Longleng" },
    { name: "Peren", lat: 25.5000, lng: 93.7333, district: "Peren" },
    { name: "Noklak", lat: 26.1000, lng: 95.0500, district: "Noklak" },
    { name: "Shamator", lat: 25.6667, lng: 94.8333, district: "Shamator" }
  ];

  const itineraries = [
    "Guwahati → Shillong → Cherrapunji", "Gangtok → Nathula → Tsomgo Lake", "Kohima → Dzukou Valley → Khonoma",
    "Aizawl → Champhai → Murlen", "Tawang → Bumla Pass → Madhuri Lake", "Kaziranga → Majuli → Jorhat",
    "Imphal → Loktak → Moirang", "Shillong → Umiam → Mawlynnong", "Dimapur → Kohima → Dzukou",
    "Agartala → Unakoti → Neermahal", "Guwahati City Tour", "Meghalaya Caves Expedition", "Assam Tea Garden Tour",
    "Nagaland Tribal Heritage Tour", "Manipur Dance & Culture Tour", "Sikkim Monastery Circuit", "Mizoram Hill Station Tour",
    "Tripura Palace & Temple Tour", "Arunachal Pradesh Adventure Trek", "Northeast Wildlife Safari"
  ];

  const statuses = ["active", "alert", "inactive", "offline"];
  const alertTypes = ["Panic SOS", "Geo-fence breach", "Route deviation", "Medical Emergency", "Lost contact", "Weather alert", "Vehicle breakdown", "Inactivity"];
  const severities = ["Critical", "High", "Medium", "Low"];

  // Generate 500 tourists
  const tourists = [];
  for (let i = 1; i <= 500; i++) {
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const nationality = nationalities[Math.floor(Math.random() * nationalities.length)];
    const phoneCode = countryPhoneCodes[nationality];
    const location = neLocations[Math.floor(Math.random() * neLocations.length)];
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    
    // Add realistic variation to coordinates
    const latVariation = (Math.random() - 0.5) * 0.02;
    const lngVariation = (Math.random() - 0.5) * 0.02;
    
    const registrationDaysAgo = Math.floor(Math.random() * 30);
    const lastUpdateMinutesAgo = Math.floor(Math.random() * 180);
    
    tourists.push({
      tourist_id: `TID-NE-2025-${String(i).padStart(4, '0')}`,
      name: `${firstName} ${lastName}`,
      nationality: nationality,
      phone: `${phoneCode} ${Math.floor(Math.random() * 9000000000) + 1000000000}`,
      last_known_location: {
        latitude: parseFloat((location.lat + latVariation).toFixed(6)),
        longitude: parseFloat((location.lng + lngVariation).toFixed(6)),
        timestamp: new Date(Date.now() - lastUpdateMinutesAgo * 60000).toISOString(),
        location_name: location.name
      },
      status: status,
      registration_time: new Date(Date.now() - registrationDaysAgo * 24 * 60 * 60000).toISOString(),
      itinerary: itineraries[Math.floor(Math.random() * itineraries.length)],
      district: location.district,
      age: Math.floor(Math.random() * 50) + 18,
      gender: Math.random() > 0.5 ? "Male" : "Female",
      group_size: Math.floor(Math.random() * 8) + 1,
      emergency_contact: `${phoneCode} ${Math.floor(Math.random() * 9000000000) + 1000000000}`,
      check_in_time: new Date(Date.now() - Math.floor(Math.random() * 24) * 60 * 60000).toISOString()
    });
  }

  // Generate 300 alerts
  const alerts = [];
  for (let i = 1; i <= 300; i++) {
    const tourist = tourists[Math.floor(Math.random() * tourists.length)];
    const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)];
    const severity = severities[Math.floor(Math.random() * severities.length)];
    const timeAgo = Math.floor(Math.random() * 1440);
    
    alerts.push({
      id: `ALR-2025-${String(i).padStart(4, '0')}`,
      type: alertType,
      severity: severity,
      location: tourist.last_known_location.location_name,
      district: tourist.district,
      timeMinutesAgo: timeAgo,
      touristId: tourist.tourist_id,
      latitude: tourist.last_known_location.latitude,
      longitude: tourist.last_known_location.longitude,
      resolved: Math.random() > 0.7,
      response_team: ["Police", "Medical", "Tourism", "Emergency"][Math.floor(Math.random() * 4)],
      priority_score: Math.floor(Math.random() * 100) + 1
    });
  }

  alerts.sort((a, b) => a.timeMinutesAgo - b.timeMinutesAgo);

  return { tourists, alerts };
};

// Generate the data
console.log('🚀 Generating 500+ dummy data entries...');
const data = generateDummyData();

// Save tourists data
fs.writeFileSync('./public/massive_tourists.json', JSON.stringify(data.tourists, null, 2));
console.log(`✅ Generated ${data.tourists.length} tourists -> ./public/massive_tourists.json`);

// Save alerts data  
fs.writeFileSync('./public/massive_alerts.json', JSON.stringify(data.alerts, null, 2));
console.log(`✅ Generated ${data.alerts.length} alerts -> ./public/massive_alerts.json`);

// Generate summary
const summary = {
  total_tourists: data.tourists.length,
  total_alerts: data.alerts.length,
  active_tourists: data.tourists.filter(t => t.status === 'active').length,
  tourists_with_alerts: data.tourists.filter(t => t.status === 'alert').length,
  critical_alerts: data.alerts.filter(a => a.severity === 'Critical').length,
  high_alerts: data.alerts.filter(a => a.severity === 'High').length,
  districts_covered: [...new Set(data.tourists.map(t => t.district))].length,
  nationalities_count: [...new Set(data.tourists.map(t => t.nationality))].length,
  generated_at: new Date().toISOString()
};

console.log(`\n📊 SUMMARY:`);
console.log(`📍 Total Tourists: ${summary.total_tourists}`);
console.log(`🚨 Total Alerts: ${summary.total_alerts}`);
console.log(`✅ Active Tourists: ${summary.active_tourists}`);
console.log(`⚠️ Tourists with Alerts: ${summary.tourists_with_alerts}`);
console.log(`🔴 Critical Alerts: ${summary.critical_alerts}`);
console.log(`🟡 High Priority Alerts: ${summary.high_alerts}`);
console.log(`🗺️ Districts Covered: ${summary.districts_covered}`);
console.log(`🌍 Nationalities: ${summary.nationalities_count}`);
console.log(`\n🎯 Dummy data generation complete! Ready for dashboard integration.`);
