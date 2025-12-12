# Torro Data Discovery System

A comprehensive data discovery and governance system that automatically discovers files in Azure Blob Storage, extracts metadata (column headers only - banking compliant), and provides a web interface for data governance.

## Features

- 🔍 **Automatic File Discovery**: Scans Azure Blob Storage containers for CSV, JSON, and Parquet files
- 🏦 **Banking Compliant**: Only extracts column headers/names - never downloads actual data rows
- 🔐 **Azure DLP PII Detection**: Uses Azure AI Language service for accurate PII detection in column names
- 📊 **Web Dashboard**: React-based frontend for viewing and managing discovered files
- 📧 **Email Notifications**: Sends notifications when new files are discovered
- 🔄 **Deduplication**: Prevents duplicate entries using ETag-based hashing
- ⚡ **Airflow Integration**: Scheduled discovery runs every minute

## Architecture

- **Backend**: Flask REST API (Python)
- **Frontend**: React + Vite + Material-UI
- **Scheduler**: Apache Airflow
- **Database**: MySQL
- **Storage**: Azure Blob Storage

## Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Azure Storage Account (with connection string)
- Gmail account (for email notifications - optional)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd torroairflow
```

### 2. Database Setup

1. Create MySQL databases:

```sql
CREATE DATABASE torro_discovery;
CREATE DATABASE airflow_metadata;
```

2. Run the migration:

```bash
mysql -u root -p torro_discovery < database/migrations/data_discovery.sql
```

### 3. Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

5. Start the backend server:

```bash
python app/main.py
```

The backend will run on `http://localhost:5001`

### 4. Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

### 5. Airflow Setup

1. Navigate to airflow directory:

```bash
cd airflow
```

2. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

**Note**: For Azure DLP PII detection, you need to create an Azure AI Language resource:
- Go to Azure Portal → Create Resource → Azure AI Language
- After creation, copy the Endpoint and Key from "Keys and Endpoint" section
- Add them to your `.env` file as `AZURE_AI_LANGUAGE_ENDPOINT` and `AZURE_AI_LANGUAGE_KEY`
- If not configured, PII detection will be disabled (system will still work)

5. Initialize Airflow database:

```bash
export AIRFLOW_HOME=$(pwd)
airflow db init
```

6. Create Airflow admin user:

```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

7. Start Airflow webserver (in one terminal):

```bash
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080
```

8. Start Airflow scheduler (in another terminal):

```bash
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

Access Airflow UI at `http://localhost:8080` (login with admin/admin)

## Environment Variables

### Airflow (.env)

Copy `airflow/.env.example` to `airflow/.env` and fill in:

- `AZURE_STORAGE_CONNECTION_STRING`: Your Azure Storage connection string
- `AZURE_STORAGE_ACCOUNT_NAME`: Your Azure Storage account name
- `AZURE_CONTAINERS`: Comma-separated container names
- `MYSQL_PASSWORD`: MySQL root password
- `SMTP_USER`: Gmail address for notifications
- `SMTP_PASSWORD`: Gmail app password (create at https://myaccount.google.com/apppasswords)
- `NOTIFICATION_EMAILS`: Comma-separated email addresses for notifications
- `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN`: Airflow database connection string
- `AIRFLOW__WEBSERVER__SECRET_KEY`: Secret key for Airflow webserver (generate with `openssl rand -hex 32`)

### Backend (.env)

Copy `backend/.env.example` to `backend/.env` and fill in:

- `SECRET_KEY`: Flask secret key (generate with `openssl rand -hex 32`)
- `MYSQL_PASSWORD`: MySQL root password
- `MYSQL_DATABASE`: Database name (default: `torro_discovery`)

## Usage

### Starting All Services

1. **Backend** (Terminal 1):
```bash
cd backend
source venv/bin/activate
python app/main.py
```

2. **Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```

3. **Airflow Webserver** (Terminal 3):
```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080
```

4. **Airflow Scheduler** (Terminal 4):
```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

### Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Airflow UI**: http://localhost:8080 (admin/admin)

### API Endpoints

- `GET /api/discovery` - List all discoveries (with pagination)
- `GET /api/discovery/<id>` - Get discovery details
- `PUT /api/discovery/<id>/approve` - Approve a discovery
- `PUT /api/discovery/<id>/reject` - Reject a discovery
- `GET /api/discovery/stats` - Get discovery statistics

## Banking Compliance

This system is designed for banking/financial data compliance:

- ✅ **Only extracts column headers/names** - never downloads actual data rows
- ✅ **Minimal bandwidth** - only 1-8KB per file (headers/schema metadata)
- ✅ **ETag-based hashing** - no full file downloads for deduplication

## Project Structure

```
torroairflow/
├── airflow/              # Airflow DAGs and utilities
│   ├── dags/            # Discovery DAG
│   ├── utils/           # Azure client, metadata extractor, etc.
│   └── config/          # Configuration files
├── backend/             # Flask REST API
│   └── app/             # Application code
├── frontend/            # React frontend
│   └── src/             # Source files
└── database/            # Database migrations
```

## Troubleshooting

### Airflow DAG not running

1. Check Airflow scheduler is running
2. Verify DAG is not paused in Airflow UI
3. Check logs: `airflow/logs/`

### Backend connection errors

1. Verify MySQL is running: `mysql -u root -p`
2. Check database exists: `SHOW DATABASES;`
3. Verify credentials in `backend/.env`

### Frontend API errors

1. Verify backend is running on port 5001
2. Check CORS settings in `backend/app/config.py`
3. Check browser console for errors

### Azure connection errors

1. Verify connection string in `airflow/.env`
2. Check Azure Storage account is accessible
3. Verify container names are correct

## Security Notes

- ⚠️ **Never commit `.env` files** - they contain sensitive credentials
- ✅ `.env` files are already in `.gitignore`
- ✅ All credentials are loaded from environment variables
- ✅ No hardcoded passwords or secrets in code

## License

[Your License Here]

## Support

For issues or questions, please contact [your-email@example.com]
