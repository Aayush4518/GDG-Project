// Comprehensive Dummy Data Generator for TravelGuardian Dashboard
// Generates 500+ realistic tourist entries with mixed factors

const generateDummyData = () => {
  // Base data for randomization
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
    "Indian": "+91",
    "American": "+1",
    "British": "+44",
    "French": "+33",
    "German": "+49",
    "Japanese": "+81",
    "Chinese": "+86",
    "Spanish": "+34",
    "Italian": "+39",
    "Australian": "+61",
    "Canadian": "+1",
    "Russian": "+7",
    "Brazilian": "+55",
    "Mexican": "+52",
    "Dutch": "+31",
    "Swiss": "+41",
    "Belgian": "+32",
    "Swedish": "+46",
    "Norwegian": "+47",
    "Danish": "+45",
    "South Korean": "+82",
    "Thai": "+66",
    "Malaysian": "+60",
    "Singaporean": "+65",
    "Indonesian": "+62",
    "Vietnamese": "+84",
    "Philippine": "+63",
    "Bangladeshi": "+880",
    "Sri Lankan": "+94",
    "Nepalese": "+977"
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
    { name: "Pelling", lat: 27.3166, lng: 88.2126, district: "West Sikkim" }
  ];

  const itineraries = [
    "Guwahati → Shillong → Cherrapunji",
    "Gangtok → Nathula → Tsomgo Lake",
    "Kohima → Dzukou Valley → Khonoma",
    "Aizawl → Champhai → Murlen",
    "Tawang → Bumla Pass → Madhuri Lake",
    "Kaziranga → Majuli → Jorhat",
    "Imphal → Loktak → Moirang",
    "Shillong → Umiam → Mawlynnong",
    "Dimapur → Kohima → Dzukou",
    "Agartala → Unakoti → Neermahal",
    "Guwahati City Tour",
    "Meghalaya Caves Expedition",
    "Assam Tea Garden Tour",
    "Nagaland Tribal Heritage Tour",
    "Manipur Dance & Culture Tour",
    "Sikkim Monastery Circuit",
    "Mizoram Hill Station Tour",
    "Tripura Palace & Temple Tour",
    "Arunachal Pradesh Adventure Trek",
    "Northeast Wildlife Safari"
  ];

  const statuses = ["active", "alert", "inactive", "offline"];
  const alertTypes = ["Panic SOS", "Geo-fence breach", "Route deviation", "Medical Emergency", "Lost contact", "Weather alert", "Vehicle breakdown", "Inactivity"];
  const severities = ["Critical", "High", "Medium", "Low"];

  // Generate tourists
  const tourists = [];
  for (let i = 1; i <= 500; i++) {
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const nationality = nationalities[Math.floor(Math.random() * nationalities.length)];
    const phoneCode = countryPhoneCodes[nationality];
    const location = neLocations[Math.floor(Math.random() * neLocations.length)];
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    
    // Add some realistic variation to coordinates
    const latVariation = (Math.random() - 0.5) * 0.01; // ±0.005 degrees
    const lngVariation = (Math.random() - 0.5) * 0.01;
    
    const registrationDaysAgo = Math.floor(Math.random() * 30); // Last 30 days
    const lastUpdateMinutesAgo = Math.floor(Math.random() * 180); // Last 3 hours
    
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
      age: Math.floor(Math.random() * 50) + 18, // Age 18-67
      gender: Math.random() > 0.5 ? "Male" : "Female",
      group_size: Math.floor(Math.random() * 8) + 1, // 1-8 people
      emergency_contact: `${phoneCode} ${Math.floor(Math.random() * 9000000000) + 1000000000}`,
      check_in_time: new Date(Date.now() - Math.floor(Math.random() * 24) * 60 * 60000).toISOString()
    });
  }

  // Generate alerts
  const alerts = [];
  for (let i = 1; i <= 200; i++) {
    const tourist = tourists[Math.floor(Math.random() * tourists.length)];
    const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)];
    const severity = severities[Math.floor(Math.random() * severities.length)];
    const timeAgo = Math.floor(Math.random() * 1440); // Last 24 hours in minutes
    
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
      resolved: Math.random() > 0.7, // 30% still active
      response_team: Math.random() > 0.5 ? "Police" : Math.random() > 0.5 ? "Medical" : "Tourism",
      priority_score: Math.floor(Math.random() * 100) + 1
    });
  }

  // Sort alerts by time (most recent first)
  alerts.sort((a, b) => a.timeMinutesAgo - b.timeMinutesAgo);

  return {
    tourists,
    alerts,
    metadata: {
      totalTourists: tourists.length,
      totalAlerts: alerts.length,
      generatedAt: new Date().toISOString(),
      dataQuality: "High",
      coverage: "Northeast India"
    }
  };
};

export default generateDummyData;
