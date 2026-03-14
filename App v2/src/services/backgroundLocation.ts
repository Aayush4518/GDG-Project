import { Platform } from 'react-native';
import * as TaskManager from 'expo-task-manager';
import * as Location from 'expo-location';
import { api } from './api';
import { storage } from './storage';

const TASK_NAME = 'background-location-task';

// Define the background task (not supported on web)
if (Platform.OS !== 'web') TaskManager.defineTask(TASK_NAME, async ({ data, error }) => {
  if (error) {
    console.error('Background location task error:', error);
    return;
  }

  if (data) {
    const { locations } = data as { locations: Location.LocationObject[] };
    const location = locations[0];

    if (location) {
      try {
        const touristId = await storage.getTouristId();
        if (touristId) {
          const body = {
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
          };
          
          await api.postLocation(touristId, body);
          console.log('Background location posted:', body);
        }
      } catch (error) {
        console.error('Failed to post background location:', error);
      }
    }
  }
});

export const startBackgroundTracking = async (): Promise<void> => {
  if (Platform.OS === 'web') {
    console.log('Background location tracking is not supported on web');
    return;
  }
  try {
    const { status } = await Location.requestBackgroundPermissionsAsync();
    if (status !== 'granted') {
      throw new Error('Background location permission not granted');
    }

    await Location.startLocationUpdatesAsync(TASK_NAME, {
      accuracy: Location.Accuracy.High,
      timeInterval: 10000,
      distanceInterval: 10,
      foregroundService: {
        notificationTitle: 'Travel Guardian is tracking your location',
        notificationBody: 'Your safety is being monitored',
        notificationColor: '#3498db',
      },
    });

    console.log('Background location tracking started');
  } catch (error) {
    console.error('Failed to start background tracking:', error);
    throw error;
  }
};

export const stopBackgroundTracking = async (): Promise<void> => {
  if (Platform.OS === 'web') return;
  try {
    await Location.stopLocationUpdatesAsync(TASK_NAME);
    console.log('Background location tracking stopped');
  } catch (error) {
    console.error('Failed to stop background tracking:', error);
    throw error;
  }
};
