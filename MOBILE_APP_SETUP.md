# FarmTwin360 Mobile App - Complete Setup Guide

This guide will help you set up and run the FarmTwin360 mobile app alongside the existing Streamlit web application.

## 🏗️ Architecture Overview

The mobile app consists of two main components:

1. **Backend API** (`mobile-backend/api.py`): FastAPI server that exposes REST endpoints
2. **Mobile App** (`mobile-app/`): React Native app built with Expo

## 📋 Prerequisites

### For Backend API
- Python 3.11+
- Existing FarmTwin360 dependencies already installed
- Additional packages: `fastapi`, `uvicorn`

### For Mobile App
- Node.js 14+ and npm
- Expo CLI
- iOS Simulator (Mac only) or Android Studio
- Expo Go app on your phone (for testing on real device)

## 🚀 Step 1: Install Backend Dependencies

```bash
pip install fastapi uvicorn python-multipart
```

These work alongside your existing Streamlit dependencies.

## 🚀 Step 2: Start the Backend API

Navigate to the mobile-backend directory and start the API server:

```bash
cd mobile-backend
python api.py
```

The API will start on `http://localhost:8000`. You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Important**: Keep this terminal window open while using the mobile app.

## 🚀 Step 3: Install Mobile App Dependencies

Open a new terminal and navigate to the mobile-app directory:

```bash
cd mobile-app
npm install
```

This will install all React Native and Expo dependencies.

## 🚀 Step 4: Configure API Endpoint

Before running the mobile app, you need to configure the API endpoint:

1. Open `mobile-app/services/api.js`
2. Find this line:
   ```javascript
   const API_URL = 'http://YOUR_BACKEND_IP:8000/api';
   ```
3. Replace `YOUR_BACKEND_IP` with:
   - **For iOS Simulator**: `localhost` or `127.0.0.1`
   - **For Android Emulator**: `10.0.2.2`
   - **For Physical Device**: Your computer's local IP address (e.g., `192.168.1.100`)

### Finding Your Local IP Address

**Windows**:
```bash
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

**Mac/Linux**:
```bash
ifconfig | grep inet
```

Example configuration:
```javascript
const API_URL = 'http://192.168.1.100:8000/api';
```

## 🚀 Step 5: Run the Mobile App

Start the Expo development server:

```bash
npm start
```

This will open the Expo Developer Tools in your browser and show a QR code.

### Option A: Run on iOS Simulator (Mac only)

Press `i` in the terminal or click "Run on iOS Simulator" in the browser.

### Option B: Run on Android Emulator

1. Make sure Android Studio and an emulator are set up
2. Press `a` in the terminal or click "Run on Android device/emulator"

### Option C: Run on Your Phone

1. Install **Expo Go** from App Store (iOS) or Play Store (Android)
2. Scan the QR code shown in the terminal/browser
3. Make sure your phone is on the same Wi-Fi network as your computer

## 🧪 Testing the App

Use these demo credentials to login:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@farmtwin.com | admin123 |
| Manager | manager@farmtwin.com | manager123 |
| Worker | worker@farmtwin.com | worker123 |
| Visitor | visitor@farmtwin.com | visitor123 |
| Veterinarian | vet@farmtwin.com | vet123 |
| Auditor | auditor@farmtwin.com | auditor123 |

## 📱 App Features

### 1. Dashboard
- View farm and barn statistics
- See recent alerts
- Quick actions for checklists and incidents

### 2. Checklist Submission
- Select farm and barn
- Enter hygiene, feed, water quality scores
- Record temperature and humidity
- GPS location automatically captured
- Add notes

### 3. Incident Reporting
- Select farm and barn
- Choose incident type
- Set severity level (Low/Medium/High)
- Describe the incident
- Document actions taken

### 4. Profile
- View user information
- Role display
- Logout functionality

## 🔧 Troubleshooting

### API Connection Failed

**Problem**: Mobile app can't connect to backend API

**Solutions**:
1. Ensure backend API is running (`python mobile-backend/api.py`)
2. Check that the IP address in `services/api.js` is correct
3. For physical devices, make sure phone and computer are on the same network
4. Disable firewall temporarily to test
5. Try accessing `http://YOUR_IP:8000/docs` in your phone's browser to verify API is reachable

### Location Permission Issues

**Problem**: GPS location not working

**Solutions**:
1. Grant location permissions when prompted
2. For iOS Simulator: Features → Location → Custom Location
3. For Android Emulator: Extended controls → Location

### App Won't Load

**Problem**: Metro bundler errors or blank screen

**Solutions**:
```bash
# Clear cache and restart
npm start -- --clear
# Or
expo start -c
```

### Port Already in Use

**Problem**: Port 8000 or 19000 already in use

**Solutions**:
```bash
# For Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# For Mac/Linux
lsof -ti:8000 | xargs kill
```

## 🔄 Running Both Web and Mobile Apps

You can run both the Streamlit web app and mobile app simultaneously:

**Terminal 1** - Streamlit Web App:
```bash
streamlit run app.py
```

**Terminal 2** - Mobile Backend API:
```bash
cd mobile-backend
python api.py
```

**Terminal 3** - Mobile App:
```bash
cd mobile-app
npm start
```

## 📦 Building Production Apps

### Android APK

```bash
cd mobile-app
expo build:android
```

### iOS IPA

```bash
cd mobile-app
expo build:ios
```

### Using EAS Build (Recommended)

```bash
npm install -g eas-cli
eas build --platform all
```

## 🌐 Network Configuration

For production deployment:

1. Deploy the FastAPI backend to a server (e.g., AWS, Heroku, DigitalOcean)
2. Update `services/api.js` with the production API URL
3. Rebuild the mobile app

Example production config:
```javascript
const API_URL = 'https://api.farmtwin360.com/api';
```

## 📂 Project Structure

```
FarmTwin360/
├── app.py                     # Streamlit web app (existing)
├── database.py                # Database models (shared)
├── models.py                  # SQLAlchemy models (shared)
├── auth.py                    # Auth utilities (shared)
│
├── mobile-backend/            # NEW: Mobile API backend
│   └── api.py                 # FastAPI REST API
│
└── mobile-app/                # NEW: React Native mobile app
    ├── App.js                 # Main app entry
    ├── app.json               # Expo config
    ├── package.json           # Dependencies
    ├── screens/               # App screens
    │   ├── LoginScreen.js
    │   ├── DashboardScreen.js
    │   ├── ChecklistScreen.js
    │   ├── IncidentScreen.js
    │   └── ProfileScreen.js
    └── services/              # API services
        └── api.js
```

## 🔐 Security Notes

1. **Change SECRET_KEY**: Update the JWT secret in both `auth.py` and `mobile-backend/api.py`
2. **HTTPS**: Use HTTPS for production API endpoints
3. **CORS**: Configure proper CORS settings for production
4. **API Rate Limiting**: Implement rate limiting on API endpoints

## 📱 Platform-Specific Notes

### iOS
- Requires Mac for native builds
- Use Expo Go for development testing
- Apple Developer Account needed for App Store distribution

### Android
- Can be built on any platform
- Use Expo Go for development testing
- Google Play Console account needed for Play Store distribution

## 🆘 Getting Help

If you encounter issues:

1. Check terminal logs in all 3 terminals (Streamlit, API, Mobile)
2. Visit Expo documentation: https://docs.expo.dev
3. Check React Navigation docs: https://reactnavigation.org
4. Review FastAPI docs: https://fastapi.tiangolo.com

## ✅ Quick Start Checklist

- [ ] Install Node.js and npm
- [ ] Install Expo CLI globally
- [ ] Install FastAPI and uvicorn via pip
- [ ] Start backend API server
- [ ] Configure API endpoint in mobile app
- [ ] Install mobile app dependencies
- [ ] Run mobile app with Expo
- [ ] Test login with demo credentials
- [ ] Submit a test checklist
- [ ] Report a test incident

## 🎉 Success!

Once everything is running, you should have:
- ✅ Streamlit web app running on http://localhost:8501
- ✅ Mobile API running on http://localhost:8000
- ✅ Mobile app running on your device/simulator
- ✅ Both apps sharing the same SQLite database

Your FarmTwin360 platform is now accessible from both web and mobile! 🌾📱
