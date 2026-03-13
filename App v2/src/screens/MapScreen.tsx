import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Dimensions,
  Alert,
  Platform,
  TextInput,
  Keyboard,
  ScrollView,
  Linking,
  Animated,
  Easing,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { Ionicons } from '@expo/vector-icons';
import * as Location from 'expo-location';
import { Vibration } from 'react-native';
import { api } from '../services/api';
import { useAppContext } from '../context/AppContext';

// Conditional import for react-native-maps (only on native platforms)
let MapView: any = null;
let Marker: any = null;
let PROVIDER_GOOGLE: any = null;
let Polygon: any = null;

if (Platform.OS !== 'web') {
  try {
    const MapsModule = require('react-native-maps');
    MapView = MapsModule.default;
    Marker = MapsModule.Marker;
    PROVIDER_GOOGLE = MapsModule.PROVIDER_GOOGLE;
    Polygon = MapsModule.Polygon;
  } catch (error) {
    console.log('Maps not available on this platform');
  }
}

type MapScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Map'>;

interface Props {
  navigation: MapScreenNavigationProp;
}

const { width, height } = Dimensions.get('window');

const riskLabelMap: Record<string, string> = {
  low: 'Low Risk',
  medium: 'Medium Risk',
  high: 'High Risk',
};

const MapScreen: React.FC<Props> = ({ navigation }) => {
  const { touristId, alertStatus } = useAppContext();
  const mapRef = useRef<any>(null);
  const [selectedLocation, setSelectedLocation] = useState<{
    latitude: number;
    longitude: number;
    title: string;
    risk?: 'low' | 'medium' | 'high';
  } | null>(null);
  const [areaSafety, setAreaSafety] = useState<'low' | 'medium' | 'high'>('low');
  const [searchQuery, setSearchQuery] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [coords, setCoords] = useState<{ latitude: number; longitude: number } | null>(null);
  const [riskZones, setRiskZones] = useState<Array<{ id: string; coordinates: Array<{ latitude: number; longitude: number }>; level: 'high' | 'medium' | 'low' }>>([]);

  // UI enhancements state
  const [elderMode, setElderMode] = useState(false);
  const [isHoldingPanic, setIsHoldingPanic] = useState(false);
  const holdProgress = useRef(new Animated.Value(0)).current;
  const pulseScale = useRef(new Animated.Value(0)).current;
  const [showPulse, setShowPulse] = useState(false);
  const holdDurationMs = 1200;
  const holdTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sample locations for demonstration with risk levels
  const sampleLocations = [
    {
      id: 1,
      latitude: 37.78825,
      longitude: -122.4324,
      title: 'Golden Gate Bridge',
      description: 'Famous suspension bridge',
      type: 'landmark',
      risk: 'low' as const,
    },
    {
      id: 2,
      latitude: 37.7849,
      longitude: -122.4094,
      title: 'Union Square',
      description: 'Shopping and entertainment district',
      type: 'shopping',
      risk: 'medium' as const,
    },
    {
      id: 3,
      latitude: 37.7749,
      longitude: -122.4194,
      title: "Fisherman's Wharf",
      description: 'Historic waterfront area',
      type: 'attraction',
      risk: 'high' as const,
    },
  ];

  const [userLocation] = useState({
    latitude: 37.7849,
    longitude: -122.4094,
  });

  // Request initial location permissions and center map
  React.useEffect(() => {
    const requestLocationPermission = async () => {
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          const loc = await Location.getCurrentPositionAsync({});
          setCoords({ latitude: loc.coords.latitude, longitude: loc.coords.longitude });
        }
      } catch (error) {
        console.error('Failed to get location:', error);
      }
    };

    requestLocationPermission();
  }, []);

  // Load risk zones (sample hardcoded until backend is ready)
  React.useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        // const zones = await api.getRiskZones();
        const zones = [
          {
            id: 'zone-1',
            level: 'high' as const,
            coordinates: [
              { latitude: 37.78925, longitude: -122.4324 },
              { latitude: 37.78925, longitude: -122.4224 },
              { latitude: 37.77925, longitude: -122.4224 },
              { latitude: 37.77925, longitude: -122.4324 },
            ],
          },
        ];
        if (mounted) setRiskZones(zones);
      } catch {}
    };
    load();
    return () => { mounted = false; };
  }, []);

  const handleLocationPress = (location: any) => {
    setSelectedLocation({
      latitude: location.latitude,
      longitude: location.longitude,
      title: location.title,
      risk: location.risk,
    });
    if (location.risk) setAreaSafety(location.risk);

    // Animate to the selected location
    mapRef.current?.animateToRegion({
      latitude: location.latitude,
      longitude: location.longitude,
      latitudeDelta: 0.01,
      longitudeDelta: 0.01,
    });
    setShowResults(false);
    Keyboard.dismiss();
  };

  const handleEmergency = async () => {
    try {
      if (!touristId) {
        Alert.alert('Not registered', 'Please register first');
        return;
      }
      let position = coords;
      if (!position) {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          const pos = await Location.getCurrentPositionAsync({});
          position = { latitude: pos.coords.latitude, longitude: pos.coords.longitude };
          setCoords(position);
        }
      }
      Vibration.vibrate(100);
      await api.postPanic(touristId, {
        latitude: position?.latitude || 0,
        longitude: position?.longitude || 0,
      });
      Alert.alert(
        'Alert has been Sent',
        'Sending Help',
        [
          { text: 'Call 100', onPress: () => { try { Linking.openURL('tel:100'); } catch {} } },
          { text: 'Cancel', style: 'cancel' },
        ]
      );
    } catch (e: any) {
      Alert.alert('Failed to send panic', e?.message ?? 'Unknown error');
    }
  };

  // Press-and-hold handlers for Panic button
  const beginHold = () => {
    if (isHoldingPanic) return;
    setIsHoldingPanic(true);
    holdProgress.setValue(0);
    Animated.timing(holdProgress, {
      toValue: 1,
      duration: holdDurationMs,
      easing: Easing.linear,
      useNativeDriver: false,
    }).start();
    holdTimer.current = setTimeout(() => {
      setIsHoldingPanic(false);
      handleEmergency();
    }, holdDurationMs);
  };
  const cancelHold = () => {
    if (!isHoldingPanic) return;
    if (holdTimer.current) clearTimeout(holdTimer.current);
    Animated.timing(holdProgress, { toValue: 0, duration: 150, useNativeDriver: false }).start(() => {
      setIsHoldingPanic(false);
    });
  };

  // Locate me pulse animation
  const triggerPulse = () => {
    setShowPulse(true);
    pulseScale.setValue(0);
    Animated.timing(pulseScale, {
      toValue: 1,
      duration: 900,
      easing: Easing.out(Easing.quad),
      useNativeDriver: false,
    }).start(() => setTimeout(() => setShowPulse(false), 600));
  };

  const getMarkerIcon = (type: string) => {
    switch (type) {
      case 'landmark':
        return 'location';
      case 'shopping':
        return 'storefront';
      case 'attraction':
        return 'camera';
      default:
        return 'location';
    }
  };

  const computeResults = (query: string) => {
    const q = query.trim().toLowerCase();
    if (!q) return [] as any[];

    if (q.includes('high')) return sampleLocations.filter(l => l.risk === 'high');
    if (q.includes('low')) return sampleLocations.filter(l => l.risk === 'low');
    if (q.includes('medium')) return sampleLocations.filter(l => l.risk === 'medium');

    return sampleLocations.filter(l => l.title.toLowerCase().includes(q));
  };

  const results = computeResults(searchQuery);

  return (
    <SafeAreaView style={styles.container}>
      {/* Alert Status Banner */}
      <View style={[
        styles.alertBanner,
        { backgroundColor: alertStatus === 'ALERT_ACTIVE' ? '#e74c3c' : '#27ae60' }
      ]}>
        <Ionicons 
          name={alertStatus === 'ALERT_ACTIVE' ? 'warning' : 'checkmark-circle'} 
          size={20} 
          color="#fff" 
        />
        <Text style={styles.alertText}>
          {alertStatus === 'ALERT_ACTIVE' 
            ? 'ALERT ACTIVE: Authorities Notified' 
            : 'System Normal: Tracking Active'
          }
        </Text>
      </View>

      <View style={styles.header}>
        <View style={{ width: 40 }} />
        <Text style={[styles.headerTitle, elderMode && { fontSize: 22 } ]}>Travel Guardian</Text>
        {/* Elder Mode toggle */}
        <TouchableOpacity style={styles.profileButton} onPress={() => setElderMode(v => !v)}>
          <Ionicons name={elderMode ? 'eye' : 'eye-outline'} size={22} color={elderMode ? '#2c3e50' : '#7f8c8d'} />
        </TouchableOpacity>
      </View>

      <View style={styles.mapContainer}>
        {Platform.OS === 'web' ? (
          <View style={styles.webMapPlaceholder}>
            <Ionicons name="map" size={64} color="#7f8c8d" />
            <Text style={styles.webMapText}>Interactive Map</Text>
            <Text style={styles.webMapSubtext}>Available on mobile devices</Text>
            <View style={styles.webMapLocations}>
              {sampleLocations.map((location) => (
                <TouchableOpacity
                  key={location.id}
                  style={styles.webLocationCard}
                  onPress={() => handleLocationPress(location)}
                >
                  <Ionicons name={getMarkerIcon(location.type) as any} size={24} color="#3498db" />
                  <View style={styles.webLocationInfo}>
                    <Text style={styles.webLocationTitle}>{location.title}</Text>
                    <Text style={styles.webLocationDescription}>{location.description}</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ) : MapView ? (
          <MapView
            ref={mapRef}
            style={styles.map}
            provider={PROVIDER_GOOGLE}
            initialRegion={{
              latitude: userLocation.latitude,
              longitude: userLocation.longitude,
              latitudeDelta: 0.0922,
              longitudeDelta: 0.0421,
            }}
            showsUserLocation={true}
            showsMyLocationButton={false}
          >
            {sampleLocations.map((location) => (
              <Marker
                key={location.id}
                coordinate={{
                  latitude: location.latitude,
                  longitude: location.longitude,
                }}
                title={location.title}
                description={location.description}
                onPress={() => handleLocationPress(location)}
              />
            ))}
            {riskZones.map((zone) => (
              <Polygon
                key={zone.id}
                coordinates={zone.coordinates}
                fillColor={zone.level === 'high' ? 'rgba(231, 76, 60, 0.25)' : 'rgba(241, 196, 15, 0.25)'}
                strokeColor={zone.level === 'high' ? '#e74c3c' : '#f1c40f'}
                strokeWidth={2}
              />
            ))}
            {showPulse && coords ? (
              <Marker coordinate={{ latitude: coords.latitude, longitude: coords.longitude }}>
                <View>
                  <Animated.View
                    style={{
                      width: 80,
                      height: 80,
                      borderRadius: 40,
                      backgroundColor: 'rgba(52,152,219,0.2)',
                      borderWidth: 2,
                      borderColor: '#3498db',
                      transform: [{ scale: pulseScale.interpolate({ inputRange: [0,1], outputRange: [0.6, 1.2] }) }],
                    }}
                  />
                </View>
              </Marker>
            ) : null}
          </MapView>
        ) : (
          <View style={styles.webMapPlaceholder}>
            <Ionicons name="map" size={64} color="#7f8c8d" />
            <Text style={styles.webMapText}>Map Loading...</Text>
          </View>
        )}

        {/* Search Bar */}
        <View style={[styles.searchContainer, elderMode && { top: 24 }] }>
          <View style={[styles.searchBar, elderMode && { paddingVertical: 12 } ]}>
            <Ionicons name="search" size={20} color="#7f8c8d" />
            <TextInput
              style={[styles.searchInput, elderMode && { fontSize: 18 } ]}
              value={searchQuery}
              onChangeText={(t) => { setSearchQuery(t); setShowResults(true); }}
              placeholder="Search places or type: high risk / low risk"
              placeholderTextColor="#7f8c8d"
              onFocus={() => setShowResults(true)}
              returnKeyType="search"
              onSubmitEditing={() => setShowResults(false)}
            />
            {!!searchQuery && (
              <TouchableOpacity onPress={() => { setSearchQuery(''); setShowResults(false); }}>
                <Ionicons name="close-circle" size={18} color="#bdc3c7" />
              </TouchableOpacity>
            )}
          </View>

          {showResults && results.length > 0 && (
            <View style={styles.resultsContainer}>
              <ScrollView keyboardShouldPersistTaps="handled">
                {results.map((r) => (
                  <TouchableOpacity key={r.id} style={styles.resultRow} onPress={() => handleLocationPress(r)}>
                    <Ionicons name={getMarkerIcon(r.type) as any} size={18} color="#3498db" />
                    <View style={{ marginLeft: 8, flex: 1 }}>
                      <Text style={[styles.resultTitle, elderMode && { fontSize: 16 } ]}>{r.title}</Text>
                      <Text style={[styles.resultSub, elderMode && { fontSize: 13 } ]}>{riskLabelMap[r.risk]}</Text>
                    </View>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          )}
        </View>

        {/* Weather + Safety Notifier (top-left) */}
        <View style={styles.notifierContainer}>
          <View style={styles.weatherCard}>
            <Ionicons name="partly-sunny" size={18} color="#f39c12" />
            <Text style={[styles.weatherText, elderMode && { fontSize: 16 } ]}>28°C · Sunny</Text>
          </View>
          <View style={[styles.safetyCard, elderMode && { paddingVertical: 10, paddingHorizontal: 14 } ]}>
            <Ionicons name="shield-checkmark" size={18} color={areaSafety === 'high' ? '#e74c3c' : areaSafety === 'medium' ? '#f39c12' : '#27ae60'} />
            <Text style={[styles.safetyTextLabel, elderMode && { fontSize: 16 } ]}>Area Safety: {riskLabelMap[areaSafety]}</Text>
          </View>
        </View>

        {/* Profile FAB (top-right, offset from top) */}
        <TouchableOpacity style={styles.profileFab} onPress={() => navigation.navigate('Profile')}>
          <Ionicons name="person-circle" size={28} color="#3498db" />
        </TouchableOpacity>

        {/* Locate Me FAB (bottom-right, above emergency button) */}
        <TouchableOpacity
          style={styles.locateFab}
          onPress={async () => {
            try {
              let current = coords;
              if (!current) {
                const { status } = await Location.requestForegroundPermissionsAsync();
                if (status !== 'granted') return;
                const pos = await Location.getCurrentPositionAsync({});
                current = { latitude: pos.coords.latitude, longitude: pos.coords.longitude };
                setCoords(current);
              }
              if (current) {
                mapRef.current?.animateToRegion({
                  latitude: current.latitude,
                  longitude: current.longitude,
                  latitudeDelta: 0.01,
                  longitudeDelta: 0.01,
                });
                triggerPulse();
              }
            } catch {}
          }}
        >
          <Ionicons name="locate" size={22} color="#3498db" />
        </TouchableOpacity>

        {/* Emergency Button: press-and-hold (inside mapContainer so absolute positioning works correctly) */}
        <TouchableOpacity
          activeOpacity={0.9}
          style={[styles.emergencyButton, elderMode && { paddingVertical: 22 } ]}
          onPressIn={beginHold}
          onPressOut={cancelHold}
        >
          <Ionicons name="alert" size={24} color="#fff" />
          <Text style={[styles.emergencyText, elderMode && { fontSize: 20 } ]}>{isHoldingPanic ? 'HOLD…' : 'EMERGENCY'}</Text>
          <View style={styles.holdBarContainer}>
            <Animated.View style={[styles.holdBarFill, { width: holdProgress.interpolate({ inputRange: [0,1], outputRange: ['0%', '100%'] }) }]} />
          </View>
        </TouchableOpacity>

        {/* Bottom Info Panel (inside mapContainer so absolute positioning works correctly) */}
        {selectedLocation && (
          <View style={[styles.infoPanel, elderMode && { padding: 24 } ]}>
            <View style={styles.infoHeader}>
              <Text style={[styles.infoTitle, elderMode && { fontSize: 20 } ]}>{selectedLocation.title}</Text>
              <TouchableOpacity onPress={() => setSelectedLocation(null)}>
                <Ionicons name="close" size={20} color="#7f8c8d" />
              </TouchableOpacity>
            </View>
            <View style={styles.infoActions}>
              <TouchableOpacity style={styles.infoButton}>
                <Ionicons name="navigate" size={16} color="#3498db" />
                <Text style={styles.infoButtonText}>Navigate</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.infoButton}>
                <Ionicons name="information-circle" size={16} color="#3498db" />
                <Text style={styles.infoButtonText}>Details</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.infoButton}>
                <Ionicons name="share" size={16} color="#3498db" />
                <Text style={styles.infoButtonText}>Share</Text>
              </TouchableOpacity>
            </View>
            <Text style={{ marginTop: 8, color: areaSafety === 'high' ? '#e74c3c' : areaSafety === 'medium' ? '#f39c12' : '#27ae60', fontWeight: '700' }}>Safety: {riskLabelMap[areaSafety]}</Text>
          </View>
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  alertBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    gap: 8,
  },
  alertText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e8ed',
  },
  menuButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  profileButton: {
    padding: 8,
  },
  mapContainer: {
    flex: 1,
    position: 'relative',
  },
  map: {
    width: '100%',
    height: '100%',
  },
  searchContainer: {
    position: 'absolute',
    top: 20,
    left: 20,
    right: 20,
    zIndex: 5,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 25,
    paddingHorizontal: 12,
    paddingVertical: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  searchPlaceholder: {
    marginLeft: 8,
    fontSize: 16,
    color: '#7f8c8d',
  },
  searchInput: {
    flex: 1,
    marginLeft: 8,
    fontSize: 16,
    color: '#2c3e50',
    paddingVertical: 4,
  },
  resultsContainer: {
    marginTop: 6,
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e1e8ed',
    maxHeight: 220,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 4,
    elevation: 3,
  },
  resultRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  resultTitle: { color: '#2c3e50', fontWeight: '700' },
  resultSub: { color: '#7f8c8d', fontSize: 12 },
  // Weather + Safety notifiers (top-left)
  notifierContainer: {
    position: 'absolute',
    top: 90, // pushed below search bar
    left: 20,
  },
  weatherCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    paddingVertical: 8,
    paddingHorizontal: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    marginBottom: 8,
  },
  weatherText: {
    marginLeft: 8,
    color: '#2c3e50',
    fontWeight: '600',
  },
  safetyCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e8f8f0',
    borderRadius: 12,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: '#c7ebda',
  },
  safetyTextLabel: {
    marginLeft: 8,
    color: '#27ae60',
    fontWeight: '700',
  },
  // Profile floating button and panel (top-right)
  profileFab: {
    position: 'absolute',
    top: 90, // pushed below search bar and away from notifications
    right: 20,
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 4,
  },
  locateFab: {
    position: 'absolute',
    right: 24,
    bottom: 100, // above emergency button
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 4,
  },
  // Removed quick actions per requirement
  emergencyButton: {
    position: 'absolute',
    bottom: 24,
    left: 24,
    right: 24,
    backgroundColor: '#e74c3c',
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.35,
    shadowRadius: 8,
    elevation: 10,
  },
  emergencyText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
    letterSpacing: 1,
  },
  infoPanel: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  infoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  infoActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  infoButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 20,
  },
  infoButtonText: {
    marginLeft: 6,
    fontSize: 14,
    color: '#3498db',
    fontWeight: '600',
  },
  // Web-specific styles
  webMapPlaceholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    padding: 20,
  },
  webMapText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginTop: 16,
    marginBottom: 8,
  },
  webMapSubtext: {
    fontSize: 16,
    color: '#7f8c8d',
    marginBottom: 30,
  },
  webMapLocations: {
    width: '100%',
    maxWidth: 400,
  },
  webLocationCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  webLocationInfo: {
    marginLeft: 12,
    flex: 1,
  },
  webLocationTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 4,
  },
  webLocationDescription: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  holdBarContainer: {
    position: 'absolute',
    left: 10,
    right: 10,
    bottom: 8,
    height: 4,
    borderRadius: 2,
    overflow: 'hidden',
    backgroundColor: 'rgba(255,255,255,0.25)'
  },
  holdBarFill: {
    height: 4,
    backgroundColor: '#fff',
  },
});

export default MapScreen;
