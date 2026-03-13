import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity, ScrollView, Platform, StatusBar, Alert, FlatList } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { storage } from '../services/storage';
import { api } from '../services/api';
import { useAppContext } from '../context/AppContext';

type ProfileScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Profile'>;

interface Props {
  navigation: ProfileScreenNavigationProp;
}

const ProfileScreen: React.FC<Props> = ({ navigation }) => {
  const { logout, touristId } = useAppContext();
  const [profile, setProfile] = React.useState<any | null>(null);
  const [recent, setRecent] = React.useState<Array<{ latitude: number; longitude: number; timestamp: string }>>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const load = async () => {
      try {
        setIsLoading(true);
        const p = await storage.getProfile();
        setProfile(p);
        if (touristId) {
          const details = await api.getTouristDetails(touristId);
          setRecent((details?.location_history || []).slice(-10).reverse());
        }
      } catch {
      } finally {
        setIsLoading(false);
      }
    };
    const unsubscribe = navigation.addListener('focus', load);
    load();
    return unsubscribe;
  }, [navigation, touristId]);

  // Skeleton components
  const SkeletonLine = ({ width = '100%' as const, height = 14 }: { width?: number | `${number}%`; height?: number }) => (
    <View style={{ width, height, backgroundColor: '#eceff1', borderRadius: 6, marginVertical: 6 }} />
  );
  const CardSkeleton = () => (
    <View style={styles.card}>
      <SkeletonLine width={140} height={16} />
      <SkeletonLine />
      <SkeletonLine />
      <SkeletonLine />
    </View>
  );

  const handleBack = () => {
    try {
      if (navigation.canGoBack()) {
        navigation.goBack();
        return;
      }
    } catch {}
    // Fallbacks if there's no stack history
    navigation.replace('Map');
  };

  const handleSignOut = async () => {
    try {
      await logout();
      Alert.alert('Signed Out', 'You have been signed out.', [
        { text: 'OK', onPress: () => navigation.reset({ index: 0, routes: [{ name: 'Registration' }] }) },
      ]);
    } catch (error) {
      Alert.alert('Error', 'Failed to sign out. Please try again.');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={handleBack}
          hitSlop={{ top: 16, left: 16, right: 16, bottom: 16 }}
          accessibilityRole="button"
          accessibilityLabel="Go back"
        >
          <Ionicons name="arrow-back" size={26} color="#2c3e50" />
        </TouchableOpacity>
        <Text style={styles.title}>Your Profile</Text>
        <View style={{ width: 26 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {isLoading ? (
          <>
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </>
        ) : (
          <>
            <View style={styles.card}>
              <Text style={styles.sectionTitle}>Personal Information</Text>
              <View style={styles.row}><Text style={styles.label}>Name</Text><Text style={styles.value}>{profile?.name || '—'}</Text></View>
              <View style={styles.row}><Text style={styles.label}>Contact Number</Text><Text style={styles.value}>{profile?.contact || '—'}</Text></View>
              <View style={styles.row}><Text style={styles.label}>Date of Birth</Text><Text style={styles.value}>{profile?.dob || '—'}</Text></View>
              <View style={styles.row}><Text style={styles.label}>Nationality</Text><Text style={styles.value}>{profile?.nationality || '—'}</Text></View>
            </View>

            <View style={styles.card}>
              <Text style={styles.sectionTitle}>Emergency Contact</Text>
              <View style={styles.row}><Text style={styles.label}>Name</Text><Text style={styles.value}>{profile?.emergency?.name || '—'}</Text></View>
              <View style={styles.row}><Text style={styles.label}>Phone</Text><Text style={styles.value}>{profile?.emergency?.phone || '—'}</Text></View>
            </View>

            <View style={styles.card}>
              <Text style={styles.sectionTitle}>Trip Details</Text>
              <View style={styles.row}><Text style={styles.label}>Trip Start Date</Text><Text style={styles.value}>{profile?.trip?.start || '—'}</Text></View>
              <View style={styles.row}><Text style={styles.label}>Trip End Date</Text><Text style={styles.value}>{profile?.trip?.end || '—'}</Text></View>
            </View>

            <View style={styles.card}>
              <Text style={styles.sectionTitle}>Document Status</Text>
              <View style={[styles.docStatus, { backgroundColor: '#e8f8f0', borderColor: '#c7ebda' }]}>
                <Ionicons name="checkmark-circle" size={20} color="#27ae60" />
                <Text style={styles.docText}>{profile ? 'Document · Pending/Uploaded' : 'Document · Pending'}</Text>
              </View>
            </View>
          </>
        )}
      </ScrollView>

      {/* Recent Activity */}
      <View style={{ paddingHorizontal: 16, paddingBottom: 8 }}>
        <Text style={[styles.sectionTitle, { marginTop: 8 }]}>Recent Activity</Text>
      </View>
      {isLoading ? (
        <View style={{ paddingHorizontal: 16, paddingBottom: 16 }}>
          <SkeletonLine />
          <SkeletonLine />
          <SkeletonLine />
        </View>
      ) : (
        <FlatList
          data={recent}
          keyExtractor={(item, index) => `${item.timestamp}-${index}`}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 16 }}
          ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
          renderItem={({ item }) => (
            <View style={styles.activityRow}>
              <Ionicons name="navigate" size={16} color="#3498db" />
              <Text style={styles.activityText}>{new Date(item.timestamp).toLocaleString()}</Text>
              <Text style={styles.activityCoords}>{item.latitude.toFixed(5)}, {item.longitude.toFixed(5)}</Text>
            </View>
          )}
          ListEmptyComponent={() => (
            <Text style={{ textAlign: 'center', color: '#7f8c8d' }}>No recent activity</Text>
          )}
        />
      )}

      {/* Sign Out Button */}
      <View style={{ padding: 16 }}>
        <TouchableOpacity
          style={styles.signOutButton}
          onPress={handleSignOut}
        >
          <Ionicons name="log-out" size={18} color="#e74c3c" />
          <Text style={styles.signOutText}>Sign Out</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa' },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 14,
    paddingTop: (Platform.OS === 'android' ? (StatusBar.currentHeight || 0) : 0) + 18,
    backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e1e8ed',
    zIndex: 10, elevation: 4,
  },
  backButton: { padding: 10 },
  title: { fontSize: 20, fontWeight: 'bold', color: '#2c3e50' },
  content: { padding: 16, gap: 12 },
  card: {
    backgroundColor: '#fff', borderRadius: 12, padding: 16,
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 6, elevation: 2
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#2c3e50', marginBottom: 10 },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#f0f0f0' },
  label: { color: '#7f8c8d', fontWeight: '600' },
  value: { color: '#2c3e50', fontWeight: '600' },
  docStatus: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 10, paddingHorizontal: 12, borderWidth: 1, borderRadius: 10 },
  docText: { marginLeft: 8, color: '#27ae60', fontWeight: '700' },
  activityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: '#e1e8ed',
    gap: 8,
  },
  activityText: { flex: 1, color: '#2c3e50', fontWeight: '600' },
  activityCoords: { color: '#7f8c8d', fontVariant: ['tabular-nums'] as any },
  signOutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 14,
    borderRadius: 12,
    backgroundColor: '#fdecea',
    borderWidth: 1,
    borderColor: '#f5c6cb',
  },
  signOutText: {
    marginLeft: 8,
    color: '#e74c3c',
    fontWeight: '700',
  },
});

export default ProfileScreen;
