# 🚀 Deployment Guide - HydroNexus Africa

This guide will help you deploy HydroNexus Africa to various cloud platforms.

## 🌐 Deployment Options

### 1. Railway (Recommended - Free Tier Available)

Railway is a modern platform that makes deployment simple and offers a generous free tier.

#### Steps:
1. **Sign up** at [railway.app](https://railway.app)
2. **Connect your GitHub repository**
3. **Create a new project** from your GitHub repo
4. **Add environment variables**:
   ```
   SECRET_KEY=your-super-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.railway.app
   DB_NAME=waterquality_db
   DB_USER=postgres
   DB_PASSWORD=your-db-password
   DB_HOST=your-db-host
   DB_PORT=5432
   ```
5. **Deploy** - Railway will automatically detect the Dockerfile and deploy

#### Access your app:
- **Main Dashboard**: `https://your-app-name.railway.app`
- **Admin Interface**: `https://your-app-name.railway.app/admin`

### 2. Heroku

#### Prerequisites:
- Heroku CLI installed
- Heroku account

#### Steps:
1. **Login to Heroku**:
   ```bash
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create your-hydronexus-app
   ```

3. **Add PostgreSQL addon**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=your-super-secret-key-here
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

6. **Run migrations**:
   ```bash
   heroku run python manage.py migrate
   ```

7. **Create superuser**:
   ```bash
   heroku run python manage.py createsuperuser
   ```

### 3. DigitalOcean App Platform

#### Steps:
1. **Sign up** at [digitalocean.com](https://digitalocean.com)
2. **Create a new app** from your GitHub repository
3. **Configure environment variables**
4. **Deploy**

### 4. AWS Elastic Beanstalk

#### Steps:
1. **Install AWS CLI and EB CLI**
2. **Initialize EB application**:
   ```bash
   eb init
   ```
3. **Create environment**:
   ```bash
   eb create production
   ```
4. **Deploy**:
   ```bash
   eb deploy
   ```

## 🔧 Environment Variables

Set these environment variables in your deployment platform:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Settings
DB_NAME=waterquality_db
DB_USER=postgres
DB_PASSWORD=your-secure-database-password
DB_HOST=your-database-host
DB_PORT=5432

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Optional: External API Keys
WEATHER_API_KEY=your-weather-api-key
MAP_API_KEY=your-map-api-key
```

## 🗄️ Database Setup

### PostgreSQL with PostGIS

Most cloud platforms provide PostgreSQL. You'll need to:

1. **Create a PostgreSQL database**
2. **Enable PostGIS extension**:
   ```sql
   CREATE EXTENSION postgis;
   ```
3. **Update database connection settings**

### Alternative: Use Railway's PostgreSQL

Railway provides PostgreSQL with PostGIS pre-installed:

1. **Add PostgreSQL service** to your Railway project
2. **Link it** to your Django app
3. **Environment variables** will be automatically set

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` to a secure random string
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Enable HTTPS/SSL
- [ ] Use strong database passwords
- [ ] Set up proper CORS settings
- [ ] Configure logging

## 📊 Monitoring and Maintenance

### Health Checks
- Monitor your app's health at `/` endpoint
- Set up uptime monitoring (UptimeRobot, Pingdom)

### Logs
- Monitor application logs for errors
- Set up log aggregation (if needed)

### Backups
- Regular database backups
- Static file backups

## 🚀 Quick Deploy Commands

### Railway (Recommended)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Link project
railway link

# 4. Deploy
railway up
```

### Heroku
```bash
# 1. Create app
heroku create your-hydronexus-app

# 2. Add database
heroku addons:create heroku-postgresql:mini

# 3. Deploy
git push heroku main

# 4. Run migrations
heroku run python manage.py migrate
```

## 🆘 Troubleshooting

### Common Issues:

1. **Static files not loading**:
   - Run `python manage.py collectstatic --noinput`
   - Check `STATIC_ROOT` configuration

2. **Database connection errors**:
   - Verify database credentials
   - Check if PostGIS extension is enabled

3. **GIS/GDAL errors**:
   - Ensure GDAL libraries are installed in the deployment environment
   - Check Dockerfile includes necessary system dependencies

4. **Port binding issues**:
   - Use `$PORT` environment variable in production
   - Don't hardcode port numbers

## 📞 Support

If you encounter issues:
1. Check the application logs
2. Verify environment variables
3. Test locally with Docker first
4. Check platform-specific documentation

---

**🌍 Your HydroNexus Africa application is now ready to monitor water quality across Africa!** 