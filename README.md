# FarmTwin 360 - Digital Farm Management Platform

A comprehensive, IoT-free digital farm management system with 3D visualization, AI-powered risk prediction, and role-based access control. Built for hackathons and ready to deploy.

![FarmTwin 360](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)

## 🌟 Overview

FarmTwin 360 is a full-stack farm management application that provides real-time digital twin visualization, manual data input workflows, AI-based risk assessment, and comprehensive compliance tracking—all without requiring IoT sensors.

**Perfect for:**
- Farm operations management
- Biosecurity compliance
- Visitor management
- Risk assessment and prevention
- Regulatory reporting
- Hackathon demonstrations

## ✨ Key Features

### 1. **Digital Twin Visualization**
- Interactive 3D farm model using Plotly
- Real-time color-coded barn risk indicators (🟢 Low, 🟡 Medium, 🔴 High)
- Spatial positioning of barns, facilities, and infrastructure
- Risk heatmap overlays

### 2. **Role-Based Access Control**
Six distinct user roles with appropriate permissions:
- **Admin**: Full system access, user management, farm configuration
- **Manager**: Dashboard access, analytics, visitor log approval
- **Worker**: Daily checklist submission, incident reporting
- **Visitor**: QR-based check-in, SOP access
- **Vet**: Analytics access, incident review, recommendations
- **Auditor**: Read-only compliance report access

### 3. **AI-Powered Risk Prediction**
- Machine learning model (Random Forest Classifier)
- Analyzes 7 key parameters: hygiene, mortality, feed quality, water quality, ventilation, temperature, humidity
- Real-time risk classification (High/Medium/Low)
- Automatic barn risk level updates
- Alert generation for high-risk conditions

### 4. **Manual Data Input**
- **Daily Checklists**: Worker submissions with GPS coordinates and photos
- **Incident Reports**: Detailed incident tracking with severity levels
- **Visitor Logs**: QR code-based visitor registration
- Photo upload capability for documentation

### 5. **Comprehensive Analytics**
- Mortality trend analysis
- Hygiene score tracking
- Risk distribution charts
- Incident analysis by type and severity
- Compliance reporting with exportable CSV/PDF
- Date range filtering for historical analysis

### 6. **Alert System**
- Automated alerts for missed checklists
- High-risk barn notifications
- High-severity incident alerts
- Unread alert badges in sidebar

### 7. **Multilingual Support**
- English and Spanish interfaces
- Easy language toggle in sidebar
- Comprehensive translation coverage

### 8. **Visitor Management**
- QR code generation for check-ins
- Biosecurity compliance tracking
- Standard Operating Procedure (SOP) display
- Health declaration and agreements
- Visitor log export functionality

## 🛠️ Technology Stack

### Frontend
- **Streamlit**: Interactive web application framework
- **Plotly**: 3D visualizations and interactive charts
- **streamlit-option-menu**: Enhanced navigation

### Backend
- **Python 3.11**: Core application logic
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Production-grade relational database

### AI/ML
- **Scikit-learn**: Machine learning for risk prediction
- **NumPy & Pandas**: Data processing and analysis
- **Joblib**: Model serialization

### Security
- **bcrypt**: Password hashing
- **PyJWT**: Token-based authentication
- Role-based access control (RBAC)

### Additional Libraries
- **qrcode**: QR code generation for visitors
- **Pillow**: Image processing
- **psycopg2-binary**: PostgreSQL adapter

## 📦 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database (or use Replit's built-in database)
- Git

### Local Installation

1. **Clone the Repository**
```bash
git clone <repository-url>
cd farmtwin-360
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

Or if using `pyproject.toml`:
```bash
pip install .
```

3. **Set Up Environment Variables**

Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/farmtwin
SESSION_SECRET=your-secret-key-here
```

4. **Initialize Database**

The application will automatically create tables and demo data on first run.

5. **Run the Application**
```bash
streamlit run app.py --server.port 5000
```

6. **Access the Application**

Open your browser and navigate to:
```
http://localhost:5000
```

## 🔐 Demo User Credentials

The application comes pre-loaded with demo users for testing:

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| Admin | admin@farmtwin.com | admin123 | Full system access |
| Manager | manager@farmtwin.com | manager123 | Dashboard + Analytics |
| Worker | worker@farmtwin.com | worker123 | Checklist + Incidents |
| Visitor | visitor@farmtwin.com | visitor123 | Check-in only |
| Vet | vet@farmtwin.com | vet123 | Analytics + Review |
| Auditor | auditor@farmtwin.com | auditor123 | Read-only reports |

## 📁 Project Structure

```
farmtwin-360/
├── app.py                      # Main application entry point
├── auth.py                     # Authentication & authorization
├── database.py                 # Database connection & demo data
├── models.py                   # SQLAlchemy database models
├── ai_engine.py                # ML risk prediction engine
├── utils.py                    # Utility functions (QR, alerts, etc.)
├── translations.py             # Multi-language support
├── components/
│   ├── admin.py               # Admin panel (user & farm management)
│   ├── analytics.py           # Analytics dashboard
│   ├── dashboard.py           # Main dashboard
│   ├── visitor.py             # Visitor check-in & SOP
│   ├── visualization.py       # 3D farm visualization
│   └── worker.py              # Worker interface (checklists & incidents)
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── uploads/                    # User-uploaded photos (auto-created)
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

## 🗄️ Database Schema

### Core Tables

**Users**
- id, name, email, password_hash, role, created_at, is_active

**Farms**
- id, name, location, description, created_at

**Barns**
- id, farm_id, name, capacity, position_x, position_y, position_z, risk_level, last_updated

**Checklists**
- id, barn_id, user_id, hygiene_score, mortality_count, feed_quality, water_quality, ventilation_score, temperature, humidity, notes, gps_lat, gps_lng, photo_path, submitted_at

**Incidents**
- id, barn_id, user_id, incident_type, severity, description, actions_taken, photo_path, resolved, reported_at

**Visitors**
- id, name, company, email, phone, purpose, qr_code, check_in_time, check_out_time, farm_id

**Alerts**
- id, type, message, severity, barn_id, user_id, read, created_at

## 🎯 Usage Guide

### For Administrators

1. **User Management**
   - Navigate to Admin Panel → User Management
   - Add new users with specific roles
   - Activate/deactivate user accounts

2. **Farm Configuration**
   - Admin Panel → Farm Management
   - Create new farms with location details
   - View barn distribution across farms

### For Workers

1. **Submit Daily Checklist**
   - Worker Interface → Submit Checklist
   - Select barn and fill in all parameters
   - Upload optional photo
   - Submit to receive AI risk prediction

2. **Report Incidents**
   - Worker Interface → Report Incident
   - Select incident type and severity
   - Provide description and actions taken
   - Upload evidence photos

### For Visitors

1. **Check-In Process**
   - Visitor Check-in → Check-in tab
   - Fill in personal and company details
   - Accept biosecurity agreements
   - Receive QR code for security checkpoints

2. **Review SOPs**
   - Navigate to SOP Guidelines tab
   - Read biosecurity requirements
   - Understand emergency procedures

### For Managers/Vets/Auditors

1. **View Analytics**
   - Analytics Dashboard
   - Select date range
   - Review risk analysis, mortality trends, hygiene scores
   - Export reports as CSV

2. **Monitor Compliance**
   - Analytics → Compliance Report
   - Check checklist completion rates
   - Identify non-compliant barns
   - Generate compliance reports

## 🚀 Deployment

### Deploy on Replit

1. Import this project to Replit
2. Replit will automatically detect dependencies
3. The PostgreSQL database is pre-configured
4. Click "Run" to start the application
5. Your app will be available at: `https://<your-repl>.replit.app`

### Deploy on Other Platforms

**Streamlit Cloud:**
```bash
# Push to GitHub
# Connect repository to Streamlit Cloud
# Add DATABASE_URL to secrets
# Deploy!
```

**Heroku:**
```bash
heroku create farmtwin-360
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

**Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["streamlit", "run", "app.py", "--server.port=5000"]
```

## 🧪 Testing

The application has been tested with end-to-end workflows:

✅ User authentication across all roles  
✅ Dashboard visualization and metrics  
✅ Admin panel user and farm management  
✅ Worker checklist submission with AI prediction  
✅ Worker incident reporting  
✅ Visitor registration with QR generation  
✅ Analytics dashboard with all chart types  
✅ Multilingual interface switching  
✅ Role-based access control enforcement  

## 🔮 Future Enhancements (Next Phase)

1. **Flutter Mobile App**
   - Offline-first architecture
   - Android and iOS support
   - Photo capture integration
   - GPS auto-detection

2. **Real-Time Notifications**
   - Firebase Cloud Messaging integration
   - SMS alerts via Twilio
   - Email notifications

3. **Advanced 3D Visualization**
   - Three.js integration
   - Enhanced farm modeling
   - Interactive facility tours

4. **Offline Data Sync**
   - Background sync mechanism
   - Conflict resolution
   - Queue management

5. **Advanced AI Models**
   - TensorFlow Lite integration
   - Predictive analytics
   - Trend forecasting

6. **Multi-Farm Management**
   - Enterprise dashboard
   - Cross-farm analytics
   - Centralized reporting

## 🤝 Contributing

This is a hackathon-ready project. Feel free to fork and enhance!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available for educational and commercial use.

## 🙏 Acknowledgments

- Built with Streamlit for rapid prototyping
- Uses Plotly for stunning visualizations
- PostgreSQL for reliable data storage
- Scikit-learn for intelligent risk prediction

## 📞 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Contact the development team
- Check the documentation wiki

---

**Built with ❤️ for modern farm management**

*FarmTwin 360 - Bringing digital transformation to agriculture, one farm at a time.*
