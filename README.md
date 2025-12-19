# Torro Data Discovery Platform - Setup Guide

## Prerequisites

### Required Software

1. **Python 3.11** (for Airflow) and **Python 3.9+** (for Backend)
   - Install: `brew install python@3.11 python@3.9` (macOS) or use your system package manager
   - Verify: `python3.11 --version` and `python3 --version`

2. **Node.js 18+** and **npm**
   - Install: `brew install node` (macOS) or download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version` and `npm --version`

3. **MySQL 8.0+**
   - Install: `brew install mysql` (macOS) or use your system package manager
   - Verify: `mysql --version`
   - Start MySQL: `brew services start mysql` (macOS) or `sudo systemctl start mysql` (Linux)

4. **Nginx** (for reverse proxy)
   - Install: `brew install nginx` (macOS) or `sudo apt-get install nginx` (Linux)
   - Verify: `nginx -v`

5. **Git**
   - Install: `brew install git` (macOS) or use your system package manager
   - Verify: `git --version`

## Quick Setup

### 1. Clone Repository

   ```bash
   git clone <repository-url>
   cd torroupdatedairflow
   ```

### 2. Database Setup

```bash
# Login to MySQL
mysql -u root -p

# Create databases
CREATE DATABASE torro_discovery;
CREATE DATABASE airflow_metadata;

# Create user (optional, or use root)
CREATE USER 'root'@'localhost' IDENTIFIED BY 'YourPassword';
GRANT ALL PRIVILEGES ON torro_discovery.* TO 'root'@'localhost';
GRANT ALL PRIVILEGES ON airflow_metadata.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Create Database Tables

```bash
# Run migration script
mysql -u root -p torro_discovery < database/migrations/data_discovery.sql
```

### 4. Environment Configuration

Create `.env` file in project root:

```bash
# Copy template (if exists) or create new
cat > .env << 'EOF'
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YourPassword
MYSQL_DATABASE=torro_discovery
MYSQL_DATABASE_AIRFLOW=airflow_metadata

# Backend Configuration
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=*

# Database Connection Pool Settings
DB_POOL_MIN=5
DB_POOL_MAX=20
DB_POOL_RECYCLE=3600

# Airflow Configuration
AIRFLOW_FERNET_KEY=generate-with-python: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow

# Azure Blob Storage Configuration
AZURE_STORAGE_ACCOUNT_NAME=your-account-name
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_CONTAINERS=
AZURE_FOLDERS=
   AZURE_ENVIRONMENT=prod
   AZURE_ENV_TYPE=production
   AZURE_DATA_SOURCE_TYPE=credit_card
   
# Email Notification Configuration
NOTIFICATION_EMAILS=email1@example.com,email2@example.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# Azure AI Language (DLP) Configuration (Optional)
AZURE_AI_LANGUAGE_ENDPOINT=
AZURE_AI_LANGUAGE_KEY=

# Frontend URL (for email notifications)
FRONTEND_URL=https://your-domain.com
EOF
```

**Important:** Replace all placeholder values with your actual credentials.

### 5. Backend Setup

   ```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -m app.main --help
```

### 6. Airflow Setup

   ```bash
cd airflow

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Set Airflow home
export AIRFLOW_HOME=$(pwd)

# Initialize Airflow database
airflow db migrate

# Create Airflow admin user
airflow users create \
     --username airflow \
    --password airflow \
     --firstname Admin \
     --lastname User \
     --role Admin \
    --email admin@example.com

# Verify installation
airflow version
```

### 7. Frontend Setup

   ```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm run build
```

### 8. Nginx Setup

   ```bash
# Copy Nginx configuration
sudo cp nginx/torro-reverse-proxy.conf /opt/homebrew/etc/nginx/servers/  # macOS Homebrew
# OR
sudo cp nginx/torro-reverse-proxy.conf /etc/nginx/sites-available/  # Linux
sudo ln -s /etc/nginx/sites-available/torro-reverse-proxy.conf /etc/nginx/sites-enabled/  # Linux

# Generate SSL certificates (for HTTPS)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Copy SSL certificates to Nginx directory
sudo cp nginx/ssl/*.pem /opt/homebrew/etc/nginx/ssl/  # macOS Homebrew
# OR
sudo cp nginx/ssl/*.pem /etc/nginx/ssl/  # Linux

# Test Nginx configuration
sudo nginx -t

# Start/Restart Nginx
sudo brew services restart nginx  # macOS Homebrew
# OR
sudo systemctl restart nginx  # Linux
```

## Running Services

### Start Backend

   ```bash
   cd backend
   source venv/bin/activate
python3 -m app.main
   ```

Backend runs on `http://0.0.0.0:5001`

### Start Frontend

   ```bash
   cd frontend
npm run dev
```

Frontend runs on `http://0.0.0.0:3000`

### Start Airflow

**Terminal 1 - Airflow Webserver:**
```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8081
```

**Terminal 2 - Airflow Scheduler:**
```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

Airflow runs on `http://0.0.0.0:8081`

### Access via Nginx (HTTPS)

- Frontend: `https://127.0.0.1/`
- Backend API: `https://127.0.0.1/api/discovery/stats`
- Airflow: `https://127.0.0.1/airflow/`

## Verification

### Check Services

```bash
# Backend
curl http://127.0.0.1:5001/health

# Backend via Nginx
curl -k https://127.0.0.1/api/health

# Frontend
curl -k https://127.0.0.1/

# Airflow
curl -k https://127.0.0.1/airflow/
```

### Test Discovery

1. **Automatic Discovery (Airflow):**
   - Upload a file to Azure Blob Storage
   - Wait 5 minutes (Airflow runs every 5 minutes)
   - Check frontend for discovered file

2. **Manual Discovery (Refresh Button):**
   - Upload a file to Azure Blob Storage
   - Click "Refresh" button in frontend
   - File should appear immediately

## Troubleshooting

### Backend won't start
- Check MySQL is running: `brew services list` (macOS) or `sudo systemctl status mysql` (Linux)
- Verify `.env` file exists and has correct MySQL credentials
- Check port 5001 is not in use: `lsof -i :5001`

### Airflow won't start
- Ensure Python 3.11 is used: `python3.11 --version`
- Check Airflow database is initialized: `airflow db check`
- Verify `AIRFLOW_HOME` is set correctly

### Frontend won't start
- Check Node.js version: `node --version` (should be 18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### Nginx errors
- Test configuration: `sudo nginx -t`
- Check SSL certificates exist: `ls -la /opt/homebrew/etc/nginx/ssl/`
- Verify ports 80/443 are not in use: `lsof -i :80` and `lsof -i :443`

### Import errors
- Ensure virtual environments are activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version matches requirements

## Project Structure

```
torroupdatedairflow/
├── backend/          # Flask backend API
│   ├── app/
│   ├── requirements.txt
│   └── venv/
├── frontend/         # React frontend
│   ├── src/
│   ├── package.json
│   └── node_modules/
├── airflow/          # Airflow DAGs and utilities
│   ├── dags/
│   ├── utils/
│   ├── config/
│   ├── requirements.txt
│   └── venv/
├── nginx/            # Nginx reverse proxy config
│   ├── torro-reverse-proxy.conf
│   └── ssl/
├── database/         # Database migrations
│   └── migrations/
└── .env              # Environment variables (create this)
```

## Ports Used

- **3000**: Frontend (Vite dev server)
- **5001**: Backend (Flask API)
- **8081**: Airflow (Webserver)
- **3306**: MySQL
- **443**: Nginx (HTTPS)
- **80**: Nginx (HTTP redirect)

## Environment Variables

All configuration is in `.env` file at project root. See step 4 for required variables.

## Next Steps

1. Configure Azure credentials in `.env`
2. Start all services (Backend, Frontend, Airflow)
3. Access via `https://127.0.0.1/`
4. Upload test files to Azure and verify discovery

