export type RegisterRequest = {
  name: string;
  kyc_hash: string;
  emergency_contact: { name: string; phone: string; relation?: string };
  trip_end_date: string;
};

export type RegisterResponse = {
  tourist_id: string;
  name: string;
  ledger_entry: {
    block_id: number;
    hash: string;
    timestamp: string;
    event: string;
  };
  message: string;
};

// Resolve API base URL with sensible defaults across platforms.
// If localhost is used on Android, route to emulator loopback (10.0.2.2).
let API_BASE: string = 'http://localhost:8000/api/v1';

try {
  // Defer require to avoid web bundling issues
  const { Platform } = require('react-native');
  const Constants = require('expo-constants').default;

  // 1) Read configured base from multiple sources
  const configuredBase: string | undefined =
    (process as any).env?.EXPO_PUBLIC_API_BASE ||
    (global as any).EXPO_PUBLIC_API_BASE ||
    (Constants?.expoConfig as any)?.extra?.EXPO_PUBLIC_API_BASE ||
    (Constants as any)?.manifest2?.extra?.expoClient?.extra?.EXPO_PUBLIC_API_BASE;

  if (configuredBase && typeof configuredBase === 'string') {
    API_BASE = configuredBase;
  }

  // 2) If base points to localhost, resolve per platform
  const isLocalhost = API_BASE.includes('localhost') || API_BASE.includes('127.0.0.1');
  if (isLocalhost) {
    if (Platform?.OS === 'android') {
      // Prefer Android emulator loopback to always reach host localhost
      API_BASE = API_BASE.replace('localhost', '10.0.2.2').replace('127.0.0.1', '10.0.2.2');
    } else {
      // Try to use Expo dev server host IP for iOS/simulator/physical device
      const hostUri: string | undefined = (Constants?.expoConfig as any)?.hostUri || (Constants as any)?.manifest2?.extra?.expoClient?.hostUri;
      if (hostUri) {
        const hostMatch = hostUri.split(':')[0];
        if (hostMatch) {
          API_BASE = `http://${hostMatch}:8000/api/v1`;
        }
      }
    }
  }

  // Log selected base in dev for easier debugging
  if ((global as any).__DEV__) {
    // eslint-disable-next-line no-console
    console.log('[api] Using API_BASE:', API_BASE);
  }
} catch (_) {
  // no-op if react-native Platform is not available
}

async function http<T>(path: string, init: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(init.headers || {}) },
      signal: controller.signal,
      ...init,
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status} @ ${API_BASE}${path}: ${text}`);
    }
    return res.json() as Promise<T>;
  } catch (err: any) {
    const reason = err?.name === 'AbortError' ? 'timeout' : err?.message || 'unknown error';
    throw new Error(`Network error @ ${API_BASE}${path}: ${reason}`);
  } finally {
    clearTimeout(timeout);
  }
}

export const api = {
  register: (body: RegisterRequest) => http<RegisterResponse>('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  postLocation: (touristId: string, body: { latitude: number; longitude: number }) =>
    http(`/tourists/${touristId}/location`, { method: 'POST', body: JSON.stringify(body) }),
  postPanic: (touristId: string, body: { latitude: number; longitude: number }) =>
    http(`/tourists/${touristId}/panic`, { method: 'POST', body: JSON.stringify(body) }),
  // Phase 4 helpers
  getRiskZones: () => http<Array<{ id: string; coordinates: Array<{ latitude: number; longitude: number }>; level: 'high' | 'medium' | 'low' }>>('/dashboard/risk-zones', { method: 'GET' }),
  getTouristDetails: (touristId: string) => http<{ location_history: Array<{ latitude: number; longitude: number; timestamp: string }> }>(`/tourists/${touristId}/details`, { method: 'GET' }),
};

export const wsUrl = () => {
  let host = (process as any).env?.EXPO_PUBLIC_WS_HOST || (global as any).EXPO_PUBLIC_WS_HOST || 'localhost:8000';
  
  try {
    const { Platform } = require('react-native');
    const Constants = require('expo-constants').default;
    
    // If host points to localhost, resolve per platform
    const isLocalhost = host.includes('localhost') || host.includes('127.0.0.1');
    if (isLocalhost) {
      if (Platform?.OS === 'android') {
        // Use Android emulator loopback to reach host localhost
        host = host.replace('localhost', '10.0.2.2').replace('127.0.0.1', '10.0.2.2');
      } else {
        // Try to use Expo dev server host IP for iOS/simulator/physical device
        const hostUri: string | undefined = (Constants?.expoConfig as any)?.hostUri || (Constants as any)?.manifest2?.extra?.expoClient?.hostUri;
        if (hostUri) {
          const hostMatch = hostUri.split(':')[0];
          if (hostMatch) {
            host = `${hostMatch}:8000`;
          }
        }
      }
    }
  } catch (_) {
    // no-op if react-native Platform is not available
  }
  
  return `ws://${host}/api/v1/dashboard/ws/dashboard`;
};
