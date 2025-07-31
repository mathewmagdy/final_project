# MedBot - AI-Powered Healthcare Navigation System

MedBot is an intelligent healthcare navigation system that uses AI to analyze patient symptoms and provide personalized department recommendations. The system features role-based dashboards for patients, doctors, and nurses, with a modern React frontend and robust Django backend.

## 🏥 Features

### For Patients
- **AI Symptom Analysis**: Describe symptoms and get instant department recommendations
- **Confidence Scoring**: AI provides confidence levels for recommendations
- **Urgency Assessment**: Automatic urgency level detection
- **Health Resources**: Educational materials and health tips
- **Emergency Access**: Quick access to emergency services

### For Doctors & Nurses
- **Professional Dashboard**: Practice overview with key statistics
- **Patient Management**: Access to patient lists and medical histories
- **Consultation Reviews**: Review AI-generated analyses
- **Analytics & Reports**: Practice performance metrics
- **Medical Oversight**: Validate and approve AI recommendations

### System Features
- **Role-Based Access**: Different interfaces for different user types
- **Secure Authentication**: JWT-based authentication system
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live status updates during analysis
- **HIPAA Compliance**: Secure handling of medical data

## 🚀 Technology Stack

### Frontend
- **React 18** with TypeScript
- **Styled Components** for styling
- **React Hook Form** for form management
- **React Router** for navigation
- **Axios** for API communication
- **React Toastify** for notifications

### Backend
- **Django 5.2** with Python
- **Django REST Framework** for API
- **PostgreSQL** database
- **JWT Authentication** with Simple JWT
- **Django CORS Headers** for cross-origin requests
- **UUID** for secure ID generation

## 📁 Project Structure

```
medbot/
├── medbot_backend/          # Django backend
│   ├── medbot/             # Main Django project
│   ├── apps/               # Django applications
│   │   ├── users/          # User management
│   │   ├── consultations/  # Medical consultations
│   │   ├── symptoms/       # Symptom analysis
│   │   ├── departments/    # Hospital departments
│   │   └── n8n_integration/ # AI workflow integration
│   ├── requirements.txt    # Python dependencies
│   └── manage.py          # Django management script
├── medbot-frontend/        # React frontend
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── services/      # API services
│   │   ├── styles/        # Styling and themes
│   │   └── types/         # TypeScript types
│   ├── package.json       # Node.js dependencies
│   └── public/           # Static assets
└── README.md             # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone git@github.com:mathewmagdy/final_project.git
   cd final_project
   ```

2. **Set up Python virtual environment**
   ```bash
   cd medbot_backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   ```bash
   # Create PostgreSQL database
   createdb medbot_db
   
   # Run migrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data**
   ```bash
   python manage.py loaddata departments
   python manage.py loaddata sample_users
   ```

7. **Start backend server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../medbot-frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## 🧪 Testing

### Sample Accounts
```
Patient Account:
- Username: patient.doe
- Password: patient123

Doctor Account:
- Username: dr.smith
- Password: doctor123
```

### Test Symptom Analysis
1. Login with patient account
2. Enter symptoms: "I have chest pain and shortness of breath"
3. Set duration: "2 hours"
4. Set pain level: "8"
5. Click "Analyze Symptoms"
6. View AI-generated recommendations

## 🔧 Configuration

### Environment Variables
Create `.env` files in both backend and frontend directories:

**Backend (.env)**
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/medbot_db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend (.env)**
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `GET /api/auth/profile/` - Get user profile

### Symptom Analysis Endpoints
- `POST /api/symptoms/analysis/analyze_symptoms/` - Analyze symptoms
- `GET /api/symptoms/analysis/{id}/analysis_status/` - Check analysis status
- `GET /api/symptoms/analysis/{id}/analysis_results/` - Get analysis results

### Department Endpoints
- `GET /api/departments/` - List all departments
- `GET /api/departments/{id}/` - Get department details

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False` in Django settings
2. Configure production database
3. Set up static file serving
4. Configure HTTPS
5. Set up monitoring and logging

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact: mathewmagdy@example.com

## ⚠️ Medical Disclaimer

MedBot is designed to assist with healthcare navigation and provide general information only. It is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions you may have regarding a medical condition. In case of emergency, call your local emergency services immediately.

---

**Built with ❤️ for better healthcare accessibility**
