import AsyncStorage from '@react-native-async-storage/async-storage';

const KEYS = {
  touristId: 'tg_tourist_id',
  profile: 'tg_profile',
};

export const storage = {
  async setTouristId(id: string) {
    await AsyncStorage.setItem(KEYS.touristId, id);
  },
  async getTouristId() {
    return AsyncStorage.getItem(KEYS.touristId);
  },
  async setProfile(profile: any) {
    await AsyncStorage.setItem(KEYS.profile, JSON.stringify(profile));
  },
  async getProfile<T = any>(): Promise<T | null> {
    const v = await AsyncStorage.getItem(KEYS.profile);
    return v ? (JSON.parse(v) as T) : null;
  },
  async clearAll() {
    await AsyncStorage.multiRemove(Object.values(KEYS));
  },
};
