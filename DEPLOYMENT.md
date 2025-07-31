# MedBot Deployment Guide

This guide provides step-by-step instructions for deploying the MedBot application in different environments.

## 🚀 Quick Start (Development)

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### 1. Clone Repository
```bash
git clone git@github.com:mathewmagdy/final_project.git
cd final_project
```

### 2. Backend Setup
```bash
cd medbot_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb medbot_db
python manage.py migrate
python manage.py createsuperuser

# Load sample data
python manage.py loaddata departments
python manage.py loaddata sample_users

# Start server
python manage.py runserver 0.0.0.0:8000
```

### 3. Frontend Setup
```bash
cd ../medbot-frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Backend
cd medbot_backend
docker build -t medbot-backend .
docker run -p 8000:8000 medbot-backend

# Frontend
cd ../medbot-frontend
docker build -t medbot-frontend .
docker run -p 3000:3000 medbot-frontend
```

## ☁️ Production Deployment

### Environment Variables

**Backend (.env)**
```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

**Frontend (.env.production)**
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
```

### Database Setup
```bash
# PostgreSQL production setup
sudo -u postgres createdb medbot_production
sudo -u postgres createuser medbot_user
sudo -u postgres psql -c "ALTER USER medbot_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE medbot_production TO medbot_user;"
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Frontend
    location / {
        root /var/www/medbot-frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Admin panel
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Static files
    location /static/ {
        alias /var/www/medbot-backend/staticfiles/;
    }
}
```

### SSL Setup with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Systemd Service (Backend)
```ini
# /etc/systemd/system/medbot.service
[Unit]
Description=MedBot Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/medbot-backend
Environment=PATH=/var/www/medbot-backend/venv/bin
ExecStart=/var/www/medbot-backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 medbot.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable medbot
sudo systemctl start medbot
sudo systemctl status medbot
```

## 📊 Monitoring & Logging

### Application Logs
```bash
# Backend logs
tail -f /var/log/medbot/django.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System service logs
journalctl -u medbot -f
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/health/

# Frontend health
curl http://localhost:3000/

# Database connection
python manage.py dbshell
```

## 🔧 Maintenance

### Database Backup
```bash
# Create backup
pg_dump medbot_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql medbot_production < backup_file.sql
```

### Update Deployment
```bash
# Pull latest changes
git pull origin main

# Backend updates
cd medbot_backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart medbot

# Frontend updates
cd ../medbot-frontend
npm install
npm run build
sudo cp -r build/* /var/www/medbot-frontend/
sudo systemctl reload nginx
```

## 🚨 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep medbot
```

**Static Files Not Loading**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data /var/www/medbot-backend/staticfiles/
```

**CORS Errors**
```python
# In settings.py, ensure correct origins
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

**Memory Issues**
```bash
# Check memory usage
free -h
htop

# Restart services
sudo systemctl restart medbot
sudo systemctl restart nginx
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_consultations_patient ON consultations_consultation(patient_id);
CREATE INDEX idx_consultations_created ON consultations_consultation(created_at);
```

### Frontend Optimization
```bash
# Build optimized production bundle
npm run build

# Analyze bundle size
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js
```

### Caching
```python
# Redis caching (settings.py)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## 🔐 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Database user permissions
- [ ] Backup encryption
- [ ] Monitor access logs

---

For additional support, please refer to the main README.md or create an issue on GitHub.
