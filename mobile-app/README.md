# FarmTwin360 Mobile App

React Native mobile application for FarmTwin360 farm management system.

## Features

- 🔐 User authentication with JWT tokens
- 📊 Dashboard with real-time farm statistics
- ✅ Digital checklist submissions with GPS tracking
- ⚠️ Incident reporting system
- 👤 User profile management
- 🌍 Multi-farm and multi-barn support
- 📱 Native iOS and Android support
- 🎨 Beautiful green-themed UI

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (for Mac) or Android Studio (for Android development)
- Expo Go app on your mobile device (for testing)

## Installation

1. Navigate to the mobile-app directory:
```bash
cd mobile-app
```

2. Install dependencies:
```bash
npm install
```

3. Configure the API endpoint:
   - Open `services/api.js`
   - Update `API_URL` with your backend server IP address:
   ```javascript
   const API_URL = 'http://YOUR_BACKEND_IP:8000/api';
   ```

## Running the Backend API

Before running the mobile app, start the FastAPI backend:

1. Navigate to the mobile-backend directory:
```bash
cd ../mobile-backend
```

2. Install Python dependencies:
```bash
pip install fastapi uvicorn pyjwt bcrypt
```

3. Start the API server:
```bash
python api.py
```

The API will run on `http://localhost:8000`

## Running the Mobile App

### Development with Expo

```bash
npm start
```

Then:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app on your phone

### Platform-specific commands

```bash
# iOS
npm run ios

# Android
npm run android

# Web
npm run web
```

## Demo Credentials

Use these credentials to test different user roles:

- **Admin**: admin@farmtwin.com / admin123
- **Manager**: manager@farmtwin.com / manager123
- **Worker**: worker@farmtwin.com / worker123
- **Visitor**: visitor@farmtwin.com / visitor123
- **Veterinarian**: vet@farmtwin.com / vet123
- **Auditor**: auditor@farmtwin.com / auditor123

## Project Structure

```
mobile-app/
├── App.js                 # Main app entry point with navigation
├── screens/
│   ├── LoginScreen.js     # Authentication screen
│   ├── DashboardScreen.js # Main dashboard
│   ├── ChecklistScreen.js # Checklist submission form
│   ├── IncidentScreen.js  # Incident reporting form
│   └── ProfileScreen.js   # User profile and logout
├── services/
│   └── api.js            # API client and services
├── app.json              # Expo configuration
└── package.json          # Dependencies
```

## Screens Overview

### Login Screen
- Email and password authentication
- JWT token storage
- Role-based access

### Dashboard
- Farm and barn statistics
- Quick action buttons
- Recent alerts display
- Pull to refresh

### Checklist Form
- Farm and barn selection
- Hygiene, feed, water quality scores
- Temperature and humidity tracking
- GPS location capture
- Notes field

### Incident Reporting
- Farm and barn selection
- Incident type categorization
- Severity levels (Low, Medium, High)
- Detailed description
- Actions taken documentation

### Profile
- User information display
- Role badge
- App information
- Logout functionality

## API Endpoints Used

- `POST /api/auth/login` - User authentication
- `GET /api/user/profile` - Get user profile
- `GET /api/farms` - List accessible farms
- `GET /api/farms/{id}/barns` - List barns for a farm
- `POST /api/checklists` - Submit checklist
- `GET /api/checklists` - Get checklist history
- `POST /api/incidents` - Report incident
- `GET /api/incidents` - Get incident history
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/alerts` - Get user alerts

## Building for Production

### Android APK

```bash
expo build:android
```

### iOS IPA

```bash
expo build:ios
```

### Standalone Apps

For full native builds, consider using EAS Build:

```bash
npm install -g eas-cli
eas build --platform all
```

## Permissions Required

- **Camera**: For capturing incident photos
- **Location**: For GPS tracking in checklists
- **Storage**: For saving photos

## Troubleshooting

### API Connection Issues
- Ensure backend is running on the correct port
- Update `API_URL` in `services/api.js`
- For physical devices, use your computer's local IP (not localhost)
- Ensure firewall allows connections on port 8000

### Location Not Working
- Grant location permissions in device settings
- For iOS simulator: Features > Location > Custom Location

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
expo start -c
```

## Technologies Used

- **React Native** - Mobile framework
- **Expo** - Development platform
- **React Navigation** - Navigation library
- **Axios** - HTTP client
- **AsyncStorage** - Local storage
- **Expo Location** - GPS tracking
- **Expo Camera** - Photo capture

## License

Copyright © 2024 FarmTwin360
