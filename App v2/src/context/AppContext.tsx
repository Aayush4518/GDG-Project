import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { storage } from '../services/storage';
import { startBackgroundTracking, stopBackgroundTracking } from '../services/backgroundLocation';
import { websocketService } from '../services/websocketService';

export type AlertStatus = 'Normal' | 'ALERT_ACTIVE';

interface AppContextType {
  touristId: string | null;
  alertStatus: AlertStatus;
  isAuthenticated: boolean;
  login: (id: string) => Promise<void>;
  logout: () => Promise<void>;
  setAlertStatus: (status: AlertStatus) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [touristId, setTouristId] = useState<string | null>(null);
  const [alertStatus, setAlertStatus] = useState<AlertStatus>('Normal');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Load persisted tourist ID on app start
  useEffect(() => {
    const loadStoredTouristId = async () => {
      try {
        const storedId = await storage.getTouristId();
        if (storedId) {
          setTouristId(storedId);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Failed to load stored tourist ID:', error);
      }
    };

    loadStoredTouristId();
  }, []);

  // Start background tracking and WebSocket when authenticated
  useEffect(() => {
    if (isAuthenticated && touristId) {
      // Start background location tracking
      startBackgroundTracking().catch(console.error);

      // Connect WebSocket for real-time alerts
      websocketService.connect((message) => {
        try {
          const data = JSON.parse(message.data);
          // Only react to alerts for the current user
          if (data?.tourist_id && data.tourist_id !== touristId) return;

          if (data.event_type === 'PANIC_ALERT' || data.event_type === 'INACTIVITY_ALERT') {
            setAlertStatus('ALERT_ACTIVE');
          } else if (data.event_type === 'ALERT_RESOLVED') {
            setAlertStatus('Normal');
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      });
    } else {
      // Stop background tracking and disconnect WebSocket when not authenticated
      stopBackgroundTracking().catch(console.error);
      websocketService.disconnect();
    }

    // Cleanup on unmount
    return () => {
      websocketService.disconnect();
    };
  }, [isAuthenticated, touristId]);

  const login = async (id: string) => {
    try {
      await storage.setTouristId(id);
      setTouristId(id);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Failed to login:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await storage.clearAll();
      setTouristId(null);
      setIsAuthenticated(false);
      setAlertStatus('Normal');
    } catch (error) {
      console.error('Failed to logout:', error);
      throw error;
    }
  };

  const value: AppContextType = {
    touristId,
    alertStatus,
    isAuthenticated,
    login,
    logout,
    setAlertStatus,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
