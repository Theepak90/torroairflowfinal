# Torro Data Discovery Platform

Complete setup guide for the Torro Data Discovery Platform - a comprehensive solution for discovering and managing data assets in Azure Blob Storage and Azure Data Lake Storage Gen2.

## Prerequisites

- **Python 3.11** (Airflow requires Python < 3.12)
- **Node.js 18+** and npm
- **MySQL 8.0+**
- **Azure Account** with Blob Storage or Data Lake Storage Gen2 access
- **Git**

## Project Structure

```
torroupdatedairflow/
├── backend/          # Flask REST API
├── frontend/         # React/Vite frontend
├── airflow/          # Apache Airflow DAGs and utilities
├── database/         # Database migrations
└── nginx/            # Nginx reverse proxy configuration
```

## Step 1: Clone Repository

   ```bash
git clone https://github.com/Theepak90/torroairflowfinal.git
   cd torroupdatedairflow
   ```

## Step 2: Database Setup

### 2.1 Install MySQL

Install MySQL if not already installed:

**macOS:**
```bash
brew install mysql
brew services start mysql
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
```

### 2.2 Create Databases

```bash
mysql -u root -p
```

In MySQL prompt:
```sql
CREATE DATABASE torro_discovery;
CREATE DATABASE airflow_metadata;
EXIT;
```

### 2.3 Run Database Migration

   ```bash
mysql -u root -p torro_discovery < database/migrations/data_discovery.sql
   ```

## Step 3: Backend Setup

### 3.1 Navigate to Backend Directory

   ```bash
cd backend
```

### 3.2 Create Virtual Environment

   ```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

### 3.3 Install Dependencies

   ```bash
pip install --upgrade pip
   pip install -r requirements.txt
   ```

### 3.4 Configure Environment Variables

Copy the template and fill in your values:

```bash
cp .env.template .env
```

Edit `backend/.env`:

```bash
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DATABASE=torro_discovery

# Flask Secret Key (change in production)
SECRET_KEY=your_flask_secret_key_here

# Database Connection Pool Settings
DB_POOL_MIN=5
DB_POOL_MAX=20
DB_POOL_RECYCLE=3600

# CORS Configuration (comma-separated list of allowed origins)
CORS_ORIGINS=https://your_frontend_domain_or_ip_here

# Backend server port
BACKEND_PORT=5001
```

### 3.5 Start Backend Server

   ```bash
   cd backend
   source venv/bin/activate
   PYTHONPATH=. python app/main.py
```

Backend will run on `http://127.0.0.1:5001`

**Note:** For production, use Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5001 'app.main:create_app("production")'
```

## Step 4: Frontend Setup

### 4.1 Navigate to Frontend Directory

   ```bash
   cd frontend
```

### 4.2 Install Dependencies

```bash
   npm install
   ```

### 4.3 Configure API Base URL

Create or edit `frontend/.env`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:5001
```

### 4.4 Start Frontend Development Server

```bash
npm run dev
```

Frontend will run on `http://127.0.0.1:3000/airflow-fe/`

## Step 5: Airflow Setup

### 5.1 Navigate to Airflow Directory

```bash
cd airflow
```

### 5.2 Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 5.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.4 Configure Environment Variables

Copy the template and fill in your values:

```bash
cp .env.template .env
```

Edit `airflow/.env`:

```bash
# MySQL Database Configuration (for Airflow metadata)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DATABASE=torro_discovery
MYSQL_DATABASE_AIRFLOW=airflow_metadata

# Azure Authentication Method: "connection_string", "service_principal", or "managed_identity"
AZURE_AUTH_METHOD=service_principal

# Azure Storage Type: "blob" or "datalake"
AZURE_STORAGE_TYPE=datalake

# Azure Storage Account Name (for Data Lake)
AZURE_STORAGE_ACCOUNT_NAME=your_datalake_account_name_here

# Data Lake ABFS Paths (comma-separated if multiple)
AZURE_DATALAKE_PATHS=abfs://your_filesystem_here@your_datalake_account_name_here.dfs.core.windows.net/your_path_here

# Service Principal credentials (REQUIRED if AZURE_AUTH_METHOD=service_principal)
AZURE_CLIENT_ID=your_service_principal_client_id_here
AZURE_CLIENT_SECRET=your_service_principal_client_secret_here
AZURE_TENANT_ID=your_azure_tenant_id_here

# Azure Blob Storage Connection String (REQUIRED if AZURE_STORAGE_TYPE=blob and AZURE_AUTH_METHOD=connection_string)
AZURE_STORAGE_CONNECTION_STRING=your_azure_blob_connection_string_here

# Azure Containers and Folders to scan (comma-separated, leave empty to scan all)
AZURE_CONTAINERS=

# Azure Folders within containers to scan (comma-separated, leave empty to scan root of containers)
AZURE_FOLDERS=

# Environment details for discovered data (for metadata classification)
AZURE_ENVIRONMENT=prod
AZURE_ENV_TYPE=production
AZURE_DATA_SOURCE_TYPE=credit_card

# Azure AI Language Service (DLP) Configuration (OPTIONAL, for advanced PII detection)
AZURE_AI_LANGUAGE_ENDPOINT=https://your_ai_language_resource.cognitiveservices.azure.com/
AZURE_AI_LANGUAGE_KEY=your_ai_language_key_here

# Email Notification Configuration (OPTIONAL, for discovery alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password_here
NOTIFICATION_EMAILS=your_email1@example.com,your_email2@example.com
EMAIL_RECIPIENTS=your_email1@example.com,your_email2@example.com

# Airflow Additional Configuration
AIRFLOW_HOME=./airflow
AIRFLOW_WEBSERVER_PORT=8080
DB_RETRY_MAX_ATTEMPTS=20

# Airflow Fernet Key for encryption (OPTIONAL, Airflow can generate automatically)
AIRFLOW_FERNET_KEY=your_airflow_fernet_key_here
```

### 5.5 Initialize Airflow Database

```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)

# Initialize Airflow metadata database
airflow db init
```

### 5.6 Create Airflow Admin User (One-time)

```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### 5.7 Start Airflow Scheduler

In a new terminal:

```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

### 5.8 Start Airflow Webserver

In another new terminal:

```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080
```

Airflow UI will be available at `http://127.0.0.1:8080/airflow/`

## Step 6: Verify Installation

### 6.1 Check Services

Open separate terminals and verify each service is running:

**Backend:**
```bash
curl http://127.0.0.1:5001/api/health
```

**Frontend:**
```bash
curl http://127.0.0.1:3000/airflow-fe/
```

**Airflow:**
```bash
curl http://127.0.0.1:8080/airflow/health
```

### 6.2 Test Manual Discovery

```bash
# Direct endpoint
curl -X POST http://127.0.0.1:5001/api/discovery/trigger \
     -H "Content-Type: application/json" \
     -d '{}'

# Through NGINX (if configured)
curl -X POST https://localhost/airflow-be/api/discovery/trigger \
     -H "Content-Type: application/json" \
     -d '{}' -k

# Expected response (202 Accepted):
# {
#   "message": "Discovery triggered successfully",
#   "status": "running"
# }
```

### 6.3 Check Airflow DAG

1. Open `http://127.0.0.1:8080/airflow/` in browser
2. Login with admin credentials
3. Find `azure_blob_discovery` DAG
4. Ensure it's **unpaused** (toggle switch should be ON)
5. DAG runs automatically every 5 minutes

## Step 7: Production Deployment (Optional)

### 7.1 Nginx Reverse Proxy Setup

For production, configure Nginx reverse proxy to serve all services on port 443 (HTTPS).

Configuration file: `nginx/torro-reverse-proxy.conf`

### 7.2 SSL Certificate

Generate SSL certificates and configure in Nginx:

   ```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/nginx-selfsigned.key \
    -out nginx/ssl/nginx-selfsigned.crt
```

## Configuration Guide

### Azure Authentication Methods

**Option 1: Service Principal (Recommended)**
- Set `AZURE_AUTH_METHOD=service_principal`
- Provide `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
- Ensure Service Principal has "Storage Blob Data Reader" role

**Option 2: Managed Identity (Azure VM only)**
- Set `AZURE_AUTH_METHOD=managed_identity`
- Ensure VM has Managed Identity enabled
- Assign "Storage Blob Data Reader" role to VM identity

**Option 3: Connection String (Legacy)**
- Set `AZURE_AUTH_METHOD=connection_string`
- Provide `AZURE_STORAGE_CONNECTION_STRING`
- Only works for Blob Storage, not Data Lake

### Storage Types

**Azure Blob Storage:**
- Set `AZURE_STORAGE_TYPE=blob`
- Configure `AZURE_CONTAINERS` and `AZURE_FOLDERS`
- Leave empty to scan all containers

**Azure Data Lake Storage Gen2:**
- Set `AZURE_STORAGE_TYPE=datalake`
- Provide `AZURE_DATALAKE_PATHS` in ABFS format:
  ```
  abfs://filesystem@account.dfs.core.windows.net/path
  ```

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Find and kill process on port 5001
lsof -ti:5001 | xargs kill -9
```

**Database connection error:**
- Verify MySQL is running: `mysql -u root -p`
- Check `.env` file has correct credentials
- Ensure database exists: `SHOW DATABASES;`

### Airflow Issues

**DAG not showing:**
- Check DAG file syntax: `python airflow/dags/azure_blob_discovery_dag.py`
- Check Airflow logs: `airflow/logs/scheduler/`
- Verify DAG is not paused in UI

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (must be 3.11)

**Scheduler not running:**
- Check if process is running: `ps aux | grep airflow`
- Check logs: `airflow/logs/scheduler/`
- Restart scheduler: `airflow scheduler`

### Frontend Issues

**API connection error:**
- Verify backend is running: `curl http://127.0.0.1:5001/api/health`
- Check `VITE_API_BASE_URL` in `.env`
- Check browser console for CORS errors

## API Endpoints

### Discovery Endpoints

- `GET /api/health` - Health check
- `GET /api/discovery` - Get all discoveries (with pagination)
- `GET /api/discovery/<id>` - Get single discovery by ID
- `GET /api/discovery/stats` - Get discovery statistics
- `POST /api/discovery/trigger` - Trigger manual discovery scan (async)
- `PUT /api/discovery/<id>/approve` - Approve a discovery
- `PUT /api/discovery/<id>/reject` - Reject a discovery

### Query Parameters

- `page` - Page number (default: 0, must be non-negative)
- `size` - Page size (default: 50, max: 100)
- `status` - Filter by status (pending, approved, rejected)
- `environment` - Filter by environment (prod, dev, test)
- `data_source_type` - Filter by data source type
- `search` - Search in file names and paths

### Trigger Endpoint

The trigger endpoint (`POST /api/discovery/trigger`) runs discovery asynchronously:
- Returns immediately with `202 Accepted` status
- Runs discovery in background thread
- Scans Azure Blob Storage and Data Lake Storage Gen2
- Updates database with new/updated discoveries
- Supports both direct endpoint and NGINX proxy routes

## DAG Schedule

The discovery DAG runs automatically:
- **Schedule:** Every 5 minutes (`*/5 * * * *`)
- **Catchup:** Disabled (no backfill)
- **Max Active Runs:** 1 (prevents overlapping runs)

## Support

For issues or questions:
1. Check logs in `airflow/logs/` and `backend/logs/`
2. Verify all environment variables are set correctly
3. Ensure all services are running
4. Check database connectivity



