# Remote Server Fix Guide

## Problem
Frontend shows errors: "Error fetching discoveries" and "Error fetching stats"
Console shows: `SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON`

This means the API is returning HTML (404 page) instead of JSON.

## Root Cause
**Backend is not running on the remote server**, or Nginx is not routing correctly.

## Quick Fix Steps

### 1. SSH into Remote Server
```bash
ssh user@40.81.235.65
```

### 2. Check if Backend is Running
```bash
# Check for backend process
ps aux | grep -E 'app.main|gunicorn|flask|python.*main'

# Check if port 5001 is listening
netstat -an | grep 5001
# OR
lsof -i :5001
```

### 3. Test Backend Directly
```bash
curl http://127.0.0.1:5001/api/discovery/stats
```

**Expected:** JSON response like `{"approved_count": "0", ...}`
**If you get:** Connection refused or timeout → Backend is NOT running

### 4. Start Backend (if not running)

#### Option A: Using Python directly
```bash
cd /path/to/backend
source venv/bin/activate
python -m app.main
```

#### Option B: Using Gunicorn (recommended for production)
```bash
cd /path/to/backend
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:5001 'app.main:create_app("development")'
```

#### Option C: Run in background with nohup
```bash
cd /path/to/backend
source venv/bin/activate
nohup python -m app.main > backend.log 2>&1 &
```

### 5. Verify Backend is Working
```bash
curl http://127.0.0.1:5001/api/discovery/stats
# Should return JSON now
```

### 6. Check Nginx Configuration
```bash
# Test Nginx config
sudo nginx -t

# Check if /api location exists
sudo cat /etc/nginx/sites-enabled/* | grep -A 10 'location /api'

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### 7. Reload Nginx
```bash
sudo nginx -s reload
```

### 8. Test from Browser
Access: `https://40.81.235.65/airflow-fe/`

The frontend should now load data correctly.

## Common Issues

### Issue 1: Backend starts but stops immediately
**Check:**
- Database connection (MySQL running?)
- Environment variables (.env file exists?)
- Python dependencies installed?

### Issue 2: Backend runs but Nginx still returns 404
**Check:**
- Nginx config file is in `/etc/nginx/sites-enabled/`
- Config has `location /api` block
- `proxy_pass http://127.0.0.1:5001;` is correct
- Nginx reloaded after config change

### Issue 3: Port 5001 already in use
```bash
# Find what's using port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>
```

## Deployment Checklist

- [ ] Backend code deployed to server
- [ ] Backend virtual environment created and activated
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend `.env` file configured
- [ ] MySQL database running and accessible
- [ ] Backend process running on port 5001
- [ ] Nginx config deployed to `/etc/nginx/sites-enabled/`
- [ ] Nginx config tested (`nginx -t`)
- [ ] Nginx reloaded (`nginx -s reload`)
- [ ] Frontend code deployed and running
- [ ] SSL certificates configured
- [ ] Firewall allows ports 80, 443, 5001

## Test Commands

```bash
# Test backend
curl http://127.0.0.1:5001/api/health
curl http://127.0.0.1:5001/api/discovery/stats

# Test via Nginx (from server)
curl -k https://127.0.0.1/api/health
curl -k https://127.0.0.1/api/discovery/stats

# Test from external (from your machine)
curl -k https://40.81.235.65/api/health
curl -k https://40.81.235.65/api/discovery/stats
```

