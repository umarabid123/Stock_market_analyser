# 🚀 Production Deployment Guide

Complete guide to deploy AI Forex Trading Assistant to production servers.

---

## 📋 Prerequisites

- Linux server (Ubuntu 20.04 LTS+ recommended)
- Python 3.10+
- Node.js 18+
- Nginx (reverse proxy)
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt - free)

---

## 🔧 Backend Deployment

### 1. Setup Python Environment

```bash
# SSH into server
ssh user@your_server_ip

# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv python3-dev

# Clone repository
git clone <your-repo-url> /var/www/ai-forex
cd /var/www/ai-forex/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Install Gunicorn (production server)
pip install gunicorn
```

### 2. Configure Environment Variables

```bash
# Create production .env
sudo nano .env
```

Add configuration:
```env
# API Keys
TWELVEDATA_API_KEY=your_production_key
OANDA_API_KEY=your_oanda_key

# Data Provider
DATA_PROVIDER=auto

# Safety
PAPER_TRADING_ONLY=true

# Logging
LOG_LEVEL=INFO

# Frontend
FRONTEND_URL=https://your-domain.com
```

### 3. Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/ai-forex-backend.service
```

Content:
```ini
[Unit]
Description=AI Forex Backend API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/ai-forex/backend
Environment="PATH=/var/www/ai-forex/backend/venv/bin"
ExecStart=/var/www/ai-forex/backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-forex-backend
sudo systemctl start ai-forex-backend

# Check status
sudo systemctl status ai-forex-backend

# View logs
sudo journalctl -u ai-forex-backend -f
```

---

## 🎨 Frontend Deployment

### 1. Build React App

```bash
# Navigate to frontend
cd /var/www/ai-forex/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Output in: frontend/dist
```

### 2. Setup Nginx

```bash
# Install Nginx
sudo apt-get install nginx

# Create configuration
sudo nano /etc/nginx/sites-available/ai-forex
```

Configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Certificate (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Root directory for React app
    root /var/www/ai-forex/frontend/dist;
    index index.html;

    # Frontend routes (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Caching for static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
}
```

### 3. Enable and Test Nginx

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/ai-forex /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Enable Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Check status
sudo systemctl status nginx
```

### 4. Setup SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 🔐 Security Hardening

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny backend port externally (only via localhost)
# Already handled by Nginx proxy
```

### 2. Update System

```bash
# Regular updates
sudo apt-get update
sudo apt-get upgrade

# Set automatic security updates
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Configure API Rate Limiting

Add to `backend/app.py` main:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## 📊 Monitoring & Logs

### 1. View Service Logs

```bash
# Backend logs
sudo journalctl -u ai-forex-backend -n 100 -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Monitor System Resources

```bash
# Install monitoring tools
sudo apt-get install htop iotop nethogs

# Monitor CPU/Memory
htop

# Monitor disk
df -h
du -sh /var/www/ai-forex
```

### 3. Health Checks

```bash
# Check backend
curl https://your-domain.com/api/health

# Check frontend
curl https://your-domain.com/
```

---

## 📈 Performance Optimization

### Backend Optimization

1. **Enable Caching**
```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend
# Configure Redis caching
```

2. **Database Connection Pooling**
```python
# If using database
# Configure connection pool size
```

3. **Async Workers**
```bash
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend Optimization

1. **Code Splitting** - Already done by Vite
2. **Image Optimization** - Use modern formats
3. **Lazy Loading** - Implement for large components
4. **CDN** - Use for static assets

---

## 🔄 Continuous Deployment

### Using GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy Backend
        run: |
          ssh user@${{ secrets.SERVER_IP }} << 'EOF'
          cd /var/www/ai-forex
          git pull origin main
          cd backend
          source venv/bin/activate
          pip install -r requirements.txt
          systemctl restart ai-forex-backend
          EOF
      
      - name: Deploy Frontend
        run: |
          ssh user@${{ secrets.SERVER_IP }} << 'EOF'
          cd /var/www/ai-forex/frontend
          npm install
          npm run build
          systemctl restart nginx
          EOF
```

---

## 🆘 Troubleshooting

### Backend not responding

```bash
# Check service status
sudo systemctl status ai-forex-backend

# Restart service
sudo systemctl restart ai-forex-backend

# Check logs
sudo journalctl -u ai-forex-backend -n 50
```

### Frontend not loading

```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### High CPU/Memory usage

```bash
# Identify processes
top

# Check backend workers
ps aux | grep gunicorn

# Reduce worker count if needed
# Edit /etc/systemd/system/ai-forex-backend.service
```

---

## 📋 Maintenance Checklist

- [ ] Daily: Monitor error logs
- [ ] Weekly: Check disk space
- [ ] Monthly: Update dependencies
  ```bash
  pip install --upgrade -r requirements.txt
  npm update
  ```
- [ ] Monthly: Review security settings
- [ ] Quarterly: Update SSL certificate (auto-renewal)
- [ ] Quarterly: Backup database (if using)

---

## 🔄 Backup Strategy

```bash
# Daily backup of code
sudo tar -czf /backups/ai-forex-$(date +%Y%m%d).tar.gz /var/www/ai-forex

# Setup cron for auto-backup
sudo crontab -e
# Add: 0 2 * * * tar -czf /backups/ai-forex-$(date +\%Y\%m\%d).tar.gz /var/www/ai-forex
```

---

## 🎯 Performance Targets

- Backend API response: < 500ms
- Frontend page load: < 2 seconds
- Uptime: 99.9%
- Error rate: < 0.1%

---

## 📞 Support URLs

- **Frontend**: https://your-domain.com
- **API Docs**: https://your-domain.com/api/docs
- **Health Check**: https://your-domain.com/api/health

---

## 🔐 .env Production Template

```env
# API Keys (production)
TWELVEDATA_API_KEY=pk_...
OANDA_API_KEY=...
FINNHUB_API_KEY=...

# Data Provider
DATA_PROVIDER=auto

# Defaults
DEFAULT_PAIR=EUR/USD
DEFAULT_TIMEFRAME=15m
DEFAULT_LOOKBACK=5d

# Safety
PAPER_TRADING_ONLY=true

# Production Settings
LOG_LEVEL=INFO
FRONTEND_URL=https://your-domain.com

# Session (if needed)
SESSION_SECRET=generate_long_random_string
```

---

**Deployment completed successfully!** 🎉

Your AI Forex Trading Assistant is now running in production and ready to serve users.
