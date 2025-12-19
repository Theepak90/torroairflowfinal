# Torro Data Discovery Platform - Setup Guide

## Prerequisites

- Python 3.9+ 
- Node.js 18+ and npm
- MySQL 8.0+
- Nginx (for reverse proxy)
- Azure Storage Account (for data discovery)
- Azure AI Language Service (optional, for PII detection)

## Quick Setup

### 1. Clone Repository

```bash
git clone https://github.com/Theepak90/torroairflowfinal.git
cd torroairflowfinal
```

### 2. MySQL Database Setup

```bash
# Login to MySQL
mysql -u root -p

# Create databases
CREATE DATABASE torro_discovery;
CREATE DATABASE airflow_metadata;

# Create user
CREATE USER 'torro_user'@'localhost' IDENTIFIED BY 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON torro_discovery.* TO 'torro_user'@'localhost';
GRANT ALL PRIVILEGES ON airflow_metadata.* TO 'torro_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Import schema
mysql -u torro_user -p torro_discovery < database/migrations/data_discovery.sql
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your MySQL password and other settings

# Run backend
python3 -m app.main
```

Backend runs on `http://127.0.0.1:5000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend runs on `http://127.0.0.1:3000`

### 5. Airflow Setup

```bash
cd airflow

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your Azure credentials, MySQL password, SMTP settings

# Initialize Airflow database
export AIRFLOW_HOME=$(pwd)
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Start Airflow webserver (in one terminal)
airflow webserver --port 8080

# Start Airflow scheduler (in another terminal)
airflow scheduler
```

Airflow runs on `http://127.0.0.1:8080`

### 6. Nginx Reverse Proxy Setup

```bash
# Copy nginx config
sudo cp nginx/torro-reverse-proxy.conf /opt/homebrew/etc/nginx/servers/

# Or for Linux:
# sudo cp nginx/torro-reverse-proxy.conf /etc/nginx/sites-available/
# sudo ln -s /etc/nginx/sites-available/torro-reverse-proxy.conf /etc/nginx/sites-enabled/

# Update SSL certificate paths in nginx/torro-reverse-proxy.conf if needed
# Generate SSL certificates if you don't have them:
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
#   -keyout nginx/ssl/key.pem \
#   -out nginx/ssl/cert.pem

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo brew services restart nginx  # macOS
# sudo systemctl restart nginx     # Linux
```

Access via:
- Frontend: `https://127.0.0.1/`
- Backend API: `https://127.0.0.1/api/discovery/stats`
- Airflow: `https://127.0.0.1/airflow/`

## Environment Variables

### Backend (.env)

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=torro_user
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
MYSQL_DATABASE=torro_discovery
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
SECRET_KEY=your-secret-key-here
```

### Airflow (.env)

```bash
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=torro_user
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
MYSQL_DATABASE=airflow_metadata

# Azure Storage
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account_name
AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
AZURE_CONTAINERS=container1,container2

# Azure AI Language (for PII detection)
AZURE_AI_LANGUAGE_ENDPOINT=https://your-language-resource.cognitiveservices.azure.com/
AZURE_AI_LANGUAGE_KEY=your_ai_language_key

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
FRONTEND_URL=https://your-domain.com
```

## Running Services

### Start All Services

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python3 -m app.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Airflow Webserver:**
```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080
```

**Terminal 4 - Airflow Scheduler:**
```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

**Terminal 5 - Nginx:**
```bash
sudo nginx  # or sudo systemctl start nginx
```

## Testing

### Test Backend Directly
```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/api/discovery/stats
```

### Test Through Nginx
```bash
curl -k https://127.0.0.1/health
curl -k https://127.0.0.1/api/discovery/stats
curl -k https://127.0.0.1/
```

## Project Structure

```
torroairflowfinal/
├── backend/              # Flask REST API
│   ├── app/
│   ├── .env.template
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   └── package.json
├── airflow/            # Airflow DAGs and utilities
│   ├── dags/
│   ├── utils/
│   ├── config/
│   ├── .env.template
│   └── requirements.txt
├── nginx/              # Nginx reverse proxy config
│   ├── torro-reverse-proxy.conf
│   └── ssl/
├── database/           # Database migrations
│   └── migrations/
└── README.md
```

## Troubleshooting

### Backend won't start
- Check MySQL is running: `mysql -u root -p`
- Verify `.env` file exists and has correct MySQL credentials
- Check port 5000 is not in use: `lsof -i :5000`

### Frontend won't start
- Check Node.js version: `node --version` (needs 18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check port 3000 is not in use: `lsof -i :3000`

### Airflow won't start
- Verify `.env` file exists in airflow directory
- Check Airflow database is initialized: `airflow db check`
- Check port 8080 is not in use: `lsof -i :8080`

### Nginx errors
- Test configuration: `sudo nginx -t`
- Check error logs: `tail -f /opt/homebrew/var/log/nginx/error.log`
- Verify SSL certificates exist: `ls -la nginx/ssl/`

### MySQL connection errors
- Verify user exists: `mysql -u torro_user -p`
- Check database exists: `mysql -u root -p -e "SHOW DATABASES;"`
- Grant permissions: `GRANT ALL PRIVILEGES ON torro_discovery.* TO 'torro_user'@'localhost';`

## Production Deployment

1. Update `.env` files with production values
2. Use production SSL certificates in `nginx/ssl/`
3. Update `server_name` in nginx config to your domain
4. Set `DEBUG=False` in backend config
5. Use production MySQL credentials
6. Configure firewall to allow ports 80, 443
7. Set up process managers (systemd, PM2, etc.) for services

## Support

For issues, create an issue on GitHub: https://github.com/Theepak90/torroairflowfinal/issues
