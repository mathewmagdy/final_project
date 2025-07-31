# MedBot Backend - Django REST API

## Project Overview
MedBot is an AI-powered healthcare navigation system that helps patients find the right medical department based on their symptoms. This Django backend provides the API infrastructure for the system.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Redis (for caching and Celery)
- n8n (for AI workflow orchestration)

### Installation

1. **Clone and Setup Virtual Environment**
```bash
cd medbot_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your database and service credentials
```

3. **Database Setup**
```bash
# Create PostgreSQL database
createdb medbot_dev

# Run migrations
python manage.py migrate
```

4. **Create Superuser**
```bash
python manage.py createsuperuser
```

5. **Run Development Server**
```bash
python manage.py runserver
```

## 📁 Project Structure

```
medbot_backend/
├── apps/                          # Django applications
│   ├── authentication/            # User authentication & JWT
│   ├── users/                     # User management & profiles
│   ├── symptoms/                  # Symptom analysis & processing
│   ├── departments/               # Medical departments
│   ├── consultations/             # Patient consultations & appointments
│   ├── healthcare_systems/        # Hospital/clinic management
│   ├── n8n_integration/           # n8n workflow integration
│   ├── admin_dashboard/           # Super admin dashboard
│   ├── clinic_dashboard/          # Clinic-specific dashboard
│   ├── analytics/                 # Analytics & reporting
│   └── notifications/             # Notification system
├── medbot/                        # Django project settings
│   ├── settings/                  # Environment-specific settings
│   │   ├── base.py               # Base settings
│   │   ├── development.py        # Development settings
│   │   └── production.py         # Production settings (to be created)
│   ├── urls.py                   # Main URL configuration
│   └── wsgi.py                   # WSGI configuration
├── logs/                         # Application logs
├── requirements.txt              # Python dependencies
├── .env                         # Environment variables
└── manage.py                    # Django management script
```

## 🔧 Key Features Implemented

### ✅ Completed
- **Django Project Setup**: Complete project structure with 11 specialized apps
- **Custom User Model**: Extended user model with healthcare-specific fields
- **Settings Architecture**: Environment-based settings (dev/prod/sqlite_dev)
- **Database Models**: Complete models for all core entities
  - Users, Departments, Healthcare Systems
  - Consultations, Appointments, Symptoms
  - n8n Integration, Analytics tracking
- **PostgreSQL Integration**: Production database setup and migrations
- **JWT Authentication**: Complete authentication system with custom serializers
- **API Endpoints**: Authentication endpoints implemented
- **n8n Integration**: Webhook handlers for AI workflow callbacks
- **CORS Configuration**: Frontend integration ready
- **Admin Interface**: Superuser created and accessible

### 🔄 In Progress
- **Symptom Analysis API**: Core symptom processing endpoints
- **Dashboard Views**: Admin and clinic dashboard APIs
- **n8n Service Layer**: AI workflow triggering service

### 📋 Next Steps
1. **Symptom Analysis API**: Implement core symptom processing endpoints
2. **n8n Service Layer**: Create AI workflow triggering service
3. **Dashboard APIs**: Build admin and clinic dashboard endpoints
4. **Testing**: Unit and integration tests
5. **API Documentation**: Set up DRF Spectacular
6. **Frontend Integration**: Connect with React frontend

### 🚀 Current Status
- **Server Running**: Django development server at http://localhost:8000
- **Database**: PostgreSQL connected and migrated
- **Admin Access**: Available at http://localhost:8000/admin (admin/admin123)
- **API Base**: http://localhost:8000/api/
- **Authentication**: JWT endpoints ready at /api/auth/

## 🏗️ Architecture

### Core Components
- **Django REST Framework**: API backend
- **PostgreSQL**: Primary database
- **Redis**: Caching and Celery broker
- **n8n**: AI workflow orchestration
- **JWT**: Authentication system
- **Celery**: Background task processing

### User Types
- **Patient**: End users seeking medical guidance
- **Doctor**: Healthcare providers
- **Clinic Admin**: Clinic management staff
- **Admin**: System administrators

### Key Models
- **User**: Extended user model with healthcare fields
- **Department**: Medical specialties and departments
- **HealthcareSystem**: Hospitals and clinics
- **Consultation**: Patient symptom analysis sessions
- **Appointment**: Scheduled medical appointments

## 🔐 Security Features
- JWT-based authentication
- CORS protection
- Environment-based configuration
- Secure password validation
- HIPAA compliance ready

## 📊 Monitoring & Logging
- Structured logging configuration
- Error tracking ready (Sentry integration)
- Performance monitoring setup
- Health check endpoints

## 🧪 Testing
```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📚 API Documentation
Once the server is running, API documentation will be available at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## 🔧 Development Commands

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver

# Django shell
python manage.py shell

# Check for issues
python manage.py check
```

## 🌐 Environment Variables

Key environment variables (see `.env.example`):
- `DEBUG`: Development mode
- `SECRET_KEY`: Django secret key
- `DB_*`: Database configuration
- `REDIS_URL`: Redis connection
- `N8N_*`: n8n integration settings
- `JWT_*`: JWT token settings

## 📝 Notes
- The project uses PostgreSQL even in development for consistency
- All models use UUID primary keys for better security
- CORS is configured for React frontend integration
- Logging is configured for both console and file output
- The project is structured for easy deployment and scaling

## 🤝 Contributing
1. Follow Django best practices
2. Write tests for new features
3. Update documentation
4. Use proper commit messages
5. Follow PEP 8 style guidelines

## 📄 License
This project is part of the MedBot healthcare navigation system.
