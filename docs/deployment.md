# Deployment Guide

This guide provides detailed instructions for deploying the Face Recognition Attendance System in different environments.

## Development Environment Setup

### Windows Setup
1. Install Python 3.11 or higher
2. Install Visual Studio Build Tools (required for dlib)
3. Clone the repository
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install dlib-19.24.1-cp311-cp311-win_amd64.whl
   ```

### Linux Setup
1. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-dev python3-pip cmake build-essential
   sudo apt-get install -y libopencv-dev python3-opencv
   ```
2. Clone repository and install Python packages:
   ```bash
   pip install -r requirements.txt
   pip install dlib
   ```

## Production Deployment

### Security Configuration
1. Change default admin password in `app.py`
2. Set up proper session secret key
3. Enable HTTPS using SSL/TLS certificates
4. Configure proper file permissions

### Server Setup
1. Use a production-grade WSGI server:
   ```bash
   pip install gunicorn  # For Linux
   pip install waitress  # For Windows
   ```

2. Configure system service (Linux):
   ```ini
   [Unit]
   Description=Face Recognition Attendance System
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/app
   ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

### Nginx Configuration (Recommended)
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/app/static;
    }
}
```

## Database Configuration

### SQLite (Default)
- No additional configuration needed
- Good for small to medium deployments
- Data stored in `attendance.csv`

### PostgreSQL (Optional Upgrade)
1. Install PostgreSQL dependencies:
   ```bash
   pip install psycopg2-binary
   ```
2. Update database configuration in settings
3. Migrate data from CSV to PostgreSQL

## Environment Variables
```bash
FLASK_ENV=production
FLASK_APP=app.py
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///attendance.db  # or PostgreSQL URL
```

## Backup Configuration

### Data Backup
1. Set up automatic backups:
   ```bash
   0 0 * * * tar -czf /backup/faces_$(date +\%Y\%m\%d).tar.gz /path/to/registered_faces/
   0 0 * * * cp /path/to/attendance.csv /backup/attendance_$(date +\%Y\%m\%d).csv
   ```

### Backup Restoration
```bash
tar -xzf backup_file.tar.gz -C /path/to/restore/
```

## Monitoring Setup

### Application Monitoring
1. Install monitoring tools:
   ```bash
   pip install flask-monitoring-dashboard
   ```
2. Configure monitoring in app:
   ```python
   import flask_monitoringdashboard as dashboard
   dashboard.bind(app)
   ```

### System Monitoring
- Set up CPU/Memory monitoring
- Configure disk space alerts
- Monitor network usage
- Set up error logging

## Performance Optimization

### Server Optimization
1. Configure worker processes:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
   ```

2. Enable caching:
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

### Image Processing Optimization
- Configure OpenCV to use GPU if available
- Optimize face detection parameters
- Configure proper image resize parameters

## Troubleshooting

### Common Issues
1. dlib Installation Errors
   - Verify Visual Studio Build Tools (Windows)
   - Install CMake and C++ compiler
   
2. Memory Issues
   - Configure proper swap space
   - Adjust worker count
   - Monitor memory usage

3. Performance Issues
   - Check CPU usage
   - Monitor database performance
   - Verify camera settings

### Logging Configuration
```python
import logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

## Scaling Considerations

### Horizontal Scaling
1. Implement load balancer
2. Set up multiple worker processes
3. Configure shared storage for face images
4. Use centralized database

### Vertical Scaling
1. Increase server resources
2. Optimize database queries
3. Implement caching
4. Use GPU acceleration