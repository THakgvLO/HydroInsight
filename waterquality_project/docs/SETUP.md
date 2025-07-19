# Setup Guide - HydroNexus Africa

This guide will help you set up HydroNexus Africa on your local machine for development or production use.

## Prerequisites

### **System Requirements**
- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 10GB free disk space
- **Docker**: Version 20.10+ with Docker Compose
- **Git**: Version 2.30+

### **Software Installation**

#### **Docker Installation**
```bash
# Windows/macOS: Download from https://www.docker.com/products/docker-desktop
# Ubuntu:
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
```

#### **Git Installation**
```bash
# Windows: Download from https://git-scm.com/
# macOS:
brew install git
# Ubuntu:
sudo apt install git
```

## Quick Setup

### **1. Clone the Repository**
```bash
git clone https://github.com/THakgvLO/hydronexus-africa.git
cd hydronexus-africa
```

### **2. Environment Configuration**
```bash
# Copy the example environment file
cp env.example .env

# Edit the environment file with your settings
nano .env  # or use your preferred editor
```

### **3. Start the Application**
```bash
# Build and start all services
docker compose up -d

# View logs to monitor startup
docker compose logs -f
```

### **4. Access the Application**
- **Main Dashboard**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **API Endpoints**: http://localhost:8000/api/

## Detailed Setup

### **Environment Variables**

Edit the `.env` file with your configuration:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=hydronexus
DB_USER=postgres
DB_PASSWORD=your-secure-database-password
DB_HOST=db
DB_PORT=5432

# External API Keys (Optional)
WEATHER_API_KEY=your-weather-api-key-here
MAP_API_KEY=your-map-api-key-here

# Security Settings
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### **Database Setup**

The application uses PostgreSQL with PostGIS extension:

```bash
# Database will be automatically created on first run
# To manually create database:
docker compose exec db psql -U postgres -c "CREATE DATABASE hydronexus;"
docker compose exec db psql -U postgres -d hydronexus -c "CREATE EXTENSION postgis;"
```

### **User Management Setup**

#### **Create Superuser**
```bash
docker compose exec django python manage.py createsuperuser
```

#### **Create Test Users (Optional)**
```bash
# Run the user creation script
docker compose exec django python manage.py shell -c "
from django.contrib.auth.models import User, Group
# Create groups
managers, _ = Group.objects.get_or_create(name='Managers')
analysts, _ = Group.objects.get_or_create(name='Analysts')
operators, _ = Group.objects.get_or_create(name='Operators')
viewers, _ = Group.objects.get_or_create(name='Viewers')

# Create users (replace passwords with secure ones)
manager_user = User.objects.create_user('manager', 'manager@example.com', 'secure-password-here')
analyst_user = User.objects.create_user('analyst', 'analyst@example.com', 'secure-password-here')
operator_user = User.objects.create_user('operator', 'operator@example.com', 'secure-password-here')
viewer_user = User.objects.create_user('viewer', 'viewer@example.com', 'secure-password-here')

# Assign groups
manager_user.groups.add(managers)
analyst_user.groups.add(analysts)
operator_user.groups.add(operators)
viewer_user.groups.add(viewers)
"
```

### **Sample Data Import (Optional)**

```bash
# Import sample water quality stations
docker compose exec django python manage.py import_stations

# Import sample water quality data
docker compose exec django python manage.py import_water_quality_data

# Generate sample analytics
docker compose exec django python manage.py calculate_analytics
```

## Development Setup

### **Code Development**
```bash
# Access Django shell
docker compose exec django python manage.py shell

# Run tests
docker compose exec django python manage.py test

# Create migrations
docker compose exec django python manage.py makemigrations

# Apply migrations
docker compose exec django python manage.py migrate

# Collect static files
docker compose exec django python manage.py collectstatic
```

### **Frontend Development**
```bash
# Access static files
cd frontend/static/

# Edit CSS/JS files
# Changes will be reflected after page refresh
```

### **Database Management**
```bash
# Access database shell
docker compose exec db psql -U postgres -d hydronexus

# Backup database
docker compose exec db pg_dump -U postgres hydronexus > backup.sql

# Restore database
docker compose exec -T db psql -U postgres -d hydronexus < backup.sql
```

## Production Setup

### **Environment Configuration**
```env
# Production settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Use strong, unique passwords
DB_PASSWORD=very-secure-production-password
SECRET_KEY=very-long-random-secret-key
```

### **SSL/HTTPS Setup**
```bash
# Configure SSL certificates
# Use Let's Encrypt or your preferred SSL provider
# Update nginx configuration for HTTPS
```

### **Backup Strategy**
```bash
# Automated database backups
docker compose exec db pg_dump -U postgres hydronexus | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# File system backups
tar -czf hydronexus_backup_$(date +%Y%m%d_%H%M%S).tar.gz . --exclude=node_modules --exclude=.git
```

## Troubleshooting

### **Common Issues**

#### **Docker Issues**
```bash
# Restart Docker services
docker compose down
docker compose up -d

# Clear Docker cache
docker system prune -a
```

#### **Database Connection Issues**
```bash
# Check database status
docker compose exec db pg_isready -U postgres

# Restart database
docker compose restart db
```

#### **Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .
```

#### **Port Conflicts**
```bash
# Check port usage
netstat -tulpn | grep :8000

# Change ports in docker-compose.yml if needed
```

### **Logs and Debugging**
```bash
# View application logs
docker compose logs django

# View database logs
docker compose logs db

# View all logs
docker compose logs -f
```

## Security Considerations

### **Production Security**
- Change all default passwords
- Use strong, unique passwords
- Enable HTTPS/SSL
- Configure firewall rules
- Regular security updates
- Monitor access logs

### **Data Protection**
- Encrypt sensitive data
- Regular backups
- Access control monitoring
- GDPR compliance measures

## Support

For additional help:
- **Documentation**: [Project Wiki](https://github.com/THakgvLO/hydronexus-africa/wiki)
- **Issues**: [GitHub Issues](https://github.com/THakgvLO/hydronexus-africa/issues)
- **Email**: [support@hydronexus.africa](mailto:support@hydronexus.africa)

---

*This setup guide ensures secure and proper installation of HydroNexus Africa.* 