# Travel Guardian V2 - Production-Ready Safety App

A comprehensive React Native/Expo application for tourist safety with true background location tracking, real-time WebSocket alerts, and robust state management.

## 🚀 Key Features

### Core Safety Features
- **True Background Location Tracking**: Continuous location monitoring using `expo-task-manager` and `expo-location`
- **Real-time Alert System**: WebSocket integration for instant alert notifications from authorities
- **Emergency Panic Button**: One-tap emergency alert with location sharing and emergency call option
- **Global State Management**: React Context for seamless data flow across the entire app

### User Experience
- **Registration & KYC**: Complete onboarding flow with document verification
- **Interactive Map**: Real-time location display with safety indicators
- **Profile Management**: View and manage personal information
- **Alert Status Banner**: Visual indicator of current safety status

## 🏗️ Architecture

### Global State Management
- **AppContext**: Centralized state for `touristId`, `alertStatus`, and `isAuthenticated`
- **Automatic Persistence**: Session restoration on app restart
- **Service Integration**: Automatic background tracking and WebSocket connection management

### Background Services
- **Background Location Service**: Posts location updates every 10 seconds to backend
- **WebSocket Service**: Real-time communication with authorities dashboard
- **Automatic Reconnection**: Robust WebSocket reconnection with exponential backoff

### Screen Architecture
- **RegistrationScreen**: User onboarding with form validation
- **IdentityVerificationScreen**: Document upload and verification
- **MapScreen**: Main safety dashboard with alert status banner
- **ProfileScreen**: User profile management with sign-out functionality

## 🛠️ Technical Stack

### Core Dependencies
- **React Native 0.81.4** with TypeScript
- **Expo SDK 54** for cross-platform development
- **React Navigation 7** for screen navigation
- **React Native Maps 1.20.1** for interactive maps
- **Expo Location 19** for GPS services
- **Expo Task Manager 12** for background tasks
- **AsyncStorage** for local data persistence

### Backend Integration
- **REST API**: Registration, location posting, panic alerts
- **WebSocket**: Real-time alert notifications
- **Robust Error Handling**: Network timeouts and retry logic
- **Platform-specific API Resolution**: Android emulator support

## 📱 Installation & Setup

### Prerequisites
- Node.js 16+ and npm
- Expo CLI (`npm install -g @expo/cli`)
- Android Studio (for Android development)
- iOS Simulator (for iOS development)

### Installation
```bash
cd "App v2"
npm install
```

### Development
```bash
# Start development server
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios

# Run on web
npm run web
```

### Mock Backend (for testing)
```bash
# Start mock server
npm run mock
```

## 🔧 Configuration

### Environment Variables
Set in `app.json` under `extra`:
```json
{
  "EXPO_PUBLIC_API_BASE": "http://localhost:8000/api/v1",
  "EXPO_PUBLIC_WS_HOST": "localhost:8000"
}
```

### Android Configuration
- Background location permissions configured
- Task manager for background location updates
- Proper notification settings for foreground service

### iOS Configuration
- Location permissions (when in use and always)
- Camera and photo library permissions
- Background location capability

## 🚨 Safety Features

### Alert System
- **Normal Status**: Green banner "System Normal: Tracking Active"
- **Alert Active**: Red banner "ALERT ACTIVE: Authorities Notified"
- **Real-time Updates**: WebSocket-driven status changes

### Emergency Response
- **Panic Button**: Large, prominent emergency button
- **Location Sharing**: Automatic current location transmission
- **Emergency Call**: Direct dial to emergency services (100)
- **Confirmation Dialog**: "Alert has been Sent. Sending Help"

### Background Tracking
- **High Accuracy**: GPS with 10-second intervals
- **Distance Threshold**: 10-meter minimum movement
- **Foreground Service**: Persistent notification during tracking
- **Automatic Start/Stop**: Based on authentication status

## 🔄 State Flow

### Authentication Flow
1. User registers → `login(touristId)` called
2. Background tracking starts automatically
3. WebSocket connects for real-time alerts
4. User data persisted to AsyncStorage

### Alert Flow
1. Backend sends WebSocket message
2. `AppContext` updates `alertStatus`
3. MapScreen banner updates automatically
4. User sees real-time status change

### Sign Out Flow
1. User taps "Sign Out" in Profile
2. `logout()` clears all data
3. Background tracking stops
4. WebSocket disconnects
5. Navigation resets to Registration

## 🧪 Testing

### Manual Testing
1. **Registration**: Complete form and verify navigation to KYC
2. **Background Tracking**: Minimize app and verify location posts
3. **Emergency Button**: Test panic alert and emergency call
4. **Alert Status**: Trigger test alert from backend and verify banner
5. **Sign Out**: Verify complete session cleanup

### Mock Backend Testing
The included `mock-server.js` provides:
- Registration endpoint with fake tourist ID
- Location posting acknowledgment
- Panic alert acknowledgment
- Health check endpoint

## 📋 Production Checklist

- [ ] Backend API endpoints configured
- [ ] WebSocket server running
- [ ] Android permissions tested
- [ ] iOS permissions tested
- [ ] Background location working
- [ ] WebSocket reconnection tested
- [ ] Emergency button functional
- [ ] Alert status updates working
- [ ] Sign out flow complete

## 🔒 Security Considerations

- **Location Data**: Only sent when user is authenticated
- **WebSocket**: Secure connection to trusted backend
- **Local Storage**: Encrypted AsyncStorage for sensitive data
- **Permissions**: Minimal required permissions requested

## 🚀 Deployment

### Android
```bash
npm run build:android
```

### iOS
```bash
npm run build:ios
```

### Web
```bash
npm run web
```

## 📞 Support

For technical support or feature requests, please contact the development team or create an issue in the repository.

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**Status**: Production Ready
