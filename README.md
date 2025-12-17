# Torro Data Discovery Platform

A comprehensive data discovery and governance platform that automatically scans Azure Blob Storage, extracts file metadata and schemas, and provides a web interface for reviewing and managing discovered data assets.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Components](#components)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Development](#development)
- [Docker Deployment](#docker-deployment)
- [Troubleshooting](#troubleshooting)

## Overview

The Torro Data Discovery Platform is designed to help organizations discover, catalog, and manage their data assets stored in Azure Blob Storage. The system:

- **Automatically scans** Azure Blob Storage containers at regular intervals
- **Extracts metadata** including file schemas, sizes, timestamps, and hashes
- **Detects changes** by comparing file hashes and schema hashes
- **Provides a web UI** for reviewing, approving, and managing discovered files
- **Sends notifications** when new files or schema changes are detected
- **Maintains a searchable catalog** of all discovered data assets

## Architecture

The platform consists of three main components:

```
┌─────────────────┐
│   Frontend      │  React + Material-UI (Port 3000)
│   (React/Vite)  │
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│    Backend      │  Flask API (Port 5000)
│   (Flask)       │
└────────┬────────┘
         │
┌────────▼────────┐
│   MySQL DB      │  Data Discovery Catalog (Port 3306)
└─────────────────┘
         ▲
         │
┌────────┴────────┐
│    Airflow      │  Discovery DAG (Port 8080)
│  (Scheduler)    │  Scans Azure Blob Storage
└─────────────────┘
```

### Component Flow

1. **Airflow DAG** (`azure_blob_discovery_dag.py`) runs every 5 minutes
2. Scans configured Azure Blob Storage containers and folders
3. Extracts file metadata and schema information (without downloading full files)
4. Compares with existing records in the database
5. Inserts new discoveries or updates changed files
6. Sends email notifications for new discoveries
7. **Backend API** serves discovery data to the frontend
8. **Frontend** displays discoveries with filtering, search, and approval workflows

## Features

### Discovery Engine
- ✅ Automatic scanning of Azure Blob Storage containers
- ✅ Support for multiple storage accounts and containers
- ✅ Folder-level scanning configuration
- ✅ File extension filtering
- ✅ Schema extraction for CSV, JSON, and Parquet files
- ✅ Change detection using file hashes (ETag-based) and schema hashes
- ✅ Batch processing to handle large numbers of files
- ✅ Retry logic with exponential backoff for database operations

### Data Catalog
- ✅ Comprehensive metadata storage (file info, schemas, storage details)
- ✅ Full-text search across file names and paths
- ✅ Filtering by status, environment, data source type
- ✅ Pagination for large result sets
- ✅ Deduplication to prevent duplicate entries

### Web Interface
- ✅ Modern React UI with Material-UI components
- ✅ Real-time statistics dashboard
- ✅ Discovery table with sorting and filtering
- ✅ Detailed view for each discovery
- ✅ Approval/rejection workflow
- ✅ Manual discovery trigger
- ✅ Auto-refresh every 30 seconds

### Notifications
- ✅ Email notifications for new discoveries
- ✅ Configurable recipient lists
- ✅ SMTP integration

## Prerequisites

- **Docker** and **Docker Compose** (for containerized deployment)
- **Python 3.9+** (for local development)
- **Node.js 18+** and **npm** (for frontend development)
- **MySQL 8.0+** (or use Docker)
- **Azure Storage Account** with connection string
- **SMTP server** credentials (for email notifications)

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd torroupdatedairflow
   ```

2. **Set up environment variables**
   
   Create `.env` files in the `airflow/` and `backend/` directories based on the `.env.example` files:
   
   **`airflow/.env`**:
   ```env
   # Azure Storage Configuration
   AZURE_STORAGE_ACCOUNT_NAME=your_account_name
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
   AZURE_CONTAINERS=container1,container2
   AZURE_FOLDERS=folder/credit_card,folder/pii
   AZURE_ENVIRONMENT=prod
   AZURE_ENV_TYPE=production
   AZURE_DATA_SOURCE_TYPE=credit_card
   
   # Database Configuration
   MYSQL_HOST=mysql
   MYSQL_PORT=3306
   MYSQL_USER=torro_user
   MYSQL_PASSWORD=torro_password
   MYSQL_DATABASE=torro_discovery
   
   # Email Notifications
   NOTIFICATION_EMAILS=admin@example.com,governor@example.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   
   # Azure AI Language (DLP) - Optional
   AZURE_AI_LANGUAGE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_AI_LANGUAGE_KEY=your_key
   ```
   
   **`backend/.env`**:
   ```env
   MYSQL_HOST=mysql
   MYSQL_PORT=3306
   MYSQL_USER=torro_user
   MYSQL_PASSWORD=torro_password
   MYSQL_DATABASE=torro_discovery
   SECRET_KEY=your-secret-key-here
   CORS_ORIGINS=http://localhost:3000
   ```

3. **Start all services**
   ```bash
   cd docker
   docker-compose up -d
   ```

4. **Initialize Airflow database** (first time only)
   ```bash
   docker exec -it torro_airflow_webserver airflow db init
   docker exec -it torro_airflow_webserver airflow users create \
     --username airflow \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com \
     --password airflow
   ```

5. **Access the services**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:5000
   - **Airflow UI**: http://localhost:8080 (username: `airflow`, password: `airflow`)

6. **Unpause the DAG**
   - Go to Airflow UI → DAGs → `azure_blob_discovery`
   - Click the play button to unpause the DAG

### Local Development Setup

1. **Set up MySQL database**
   ```bash
   mysql -u root -p
   CREATE DATABASE torro_discovery;
   source database/migrations/data_discovery.sql
   ```

2. **Set up Python virtual environment (Airflow)**
   ```bash
   cd airflow
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Python virtual environment (Backend)**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Set up Frontend**
   ```bash
   cd frontend
   npm install
   ```

5. **Run services**
   - **Backend**: `cd backend && python -m app.main`
   - **Frontend**: `cd frontend && npm run dev`
   - **Airflow**: Follow Airflow installation guide for local setup

## Configuration

### Azure Storage Configuration

Configure storage accounts in `airflow/config/azure_config.py` or via environment variables:

```python
AZURE_STORAGE_ACCOUNTS = [
    {
        "name": "account1",
        "connection_string": "...",
        "containers": ["container1", "container2"],
        "folders": ["folder/path1", "folder/path2"],  # Empty string "" = root
        "environment": "prod",
        "env_type": "production",
        "data_source_type": "credit_card",
        "file_extensions": None  # None = all files, or ["csv", "json", "parquet"]
    }
]
```

### Airflow DAG Schedule

The discovery DAG runs every 5 minutes by default. To change:
- Edit `schedule_interval` in `airflow/dags/azure_blob_discovery_dag.py`
- Use cron syntax: `'*/5 * * * *'` (every 5 minutes)

### Database Connection Pool

Configure in `backend/app/config.py`:
- `DB_POOL_MIN`: Minimum connections (default: 5)
- `DB_POOL_MAX`: Maximum connections (default: 20)
- `DB_POOL_RECYCLE`: Connection recycle time in seconds (default: 3600)

## Project Structure

```
torroupdatedairflow/
├── airflow/                    # Airflow DAGs and utilities
│   ├── dags/
│   │   └── azure_blob_discovery_dag.py  # Main discovery DAG
│   ├── config/
│   │   └── azure_config.py      # Azure storage configuration
│   ├── utils/
│   │   ├── azure_blob_client.py # Azure Blob Storage client
│   │   ├── metadata_extractor.py # File metadata extraction
│   │   ├── deduplication.py     # Deduplication logic
│   │   ├── email_notifier.py   # Email notification
│   │   └── azure_dlp_client.py # Azure DLP integration (optional)
│   ├── requirements.txt
│   └── .env.example
│
├── backend/                     # Flask REST API
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   └── discovery.py # API endpoints
│   │   │   └── schemas/
│   │   │       └── discovery.py # Pydantic schemas
│   │   ├── models/
│   │   │   └── discovery.py     # Database models
│   │   ├── services/
│   │   │   └── discovery_service.py # Business logic
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database connection pool
│   │   └── main.py              # Flask app entry point
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── DiscoveryTable.jsx
│   │   │   ├── DiscoveryFilters.jsx
│   │   │   ├── SummaryCards.jsx
│   │   │   └── DiscoveryDetailsDialog.jsx
│   │   ├── pages/
│   │   │   └── DataDiscoveryPage.jsx
│   │   ├── services/
│   │   │   └── api.js           # API client
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── database/
│   └── migrations/
│       └── data_discovery.sql  # Database schema
│
├── docker/
│   ├── docker-compose.yml       # Production compose file
│   ├── docker-compose.dev.yml   # Development compose file
│   ├── Dockerfile.airflow
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
│
└── README.md
```

## Components

### Airflow DAG (`azure_blob_discovery_dag.py`)

The main discovery workflow:

1. **`discover_azure_blobs`** task:
   - Scans all configured Azure storage accounts
   - Lists blobs in specified containers and folders
   - Extracts metadata (file size, ETag, timestamps)
   - Gets file samples (1KB for CSV/JSON, 8KB tail for Parquet)
   - Extracts schema information
   - Generates file hash (ETag-based) and schema hash
   - Checks for existing records in database
   - Inserts new discoveries or updates changed files
   - Processes files in batches of 100

2. **`notify_data_governors`** task:
   - Sends email notifications for new discoveries
   - Includes summary of new files

**Key Features:**
- Retry logic with exponential backoff for database operations
- Batch processing to handle large file counts
- Schema change detection
- No full file downloads (compliance-friendly)

### Backend API (Flask)

RESTful API endpoints:

- `GET /api/discovery` - List discoveries with filtering and pagination
- `GET /api/discovery/<id>` - Get discovery details
- `PUT /api/discovery/<id>/approve` - Approve a discovery
- `PUT /api/discovery/<id>/reject` - Reject a discovery
- `GET /api/discovery/stats` - Get summary statistics
- `POST /api/discovery/trigger` - Manually trigger discovery scan
- `GET /health` - Health check

**Features:**
- Connection pooling for MySQL
- Input validation with Pydantic schemas
- CORS support
- Error handling and logging

### Frontend (React)

Modern web interface built with:
- **React 19** with hooks
- **Material-UI (MUI)** for components
- **Vite** for build tooling
- **React Router** for navigation

**Features:**
- Real-time statistics dashboard
- Searchable and filterable discovery table
- Pagination
- Approval/rejection workflow
- Auto-refresh every 30 seconds
- Manual discovery trigger
- Detailed discovery view dialog

## API Documentation

### Get Discoveries

```http
GET /api/discovery?page=0&size=50&status=pending&environment=prod&data_source_type=credit_card&search=file.csv
```

**Query Parameters:**
- `page` (int): Page number (0-indexed)
- `size` (int): Page size (1-100, default: 50)
- `status` (string, optional): Filter by status (`pending`, `approved`, `rejected`, `published`, `archived`)
- `environment` (string, optional): Filter by environment
- `data_source_type` (string, optional): Filter by data source type
- `search` (string, optional): Full-text search in file names and paths

**Response:**
```json
{
  "discoveries": [
    {
      "id": 1,
      "file_name": "data.csv",
      "storage_path": "folder/data.csv",
      "file_size_bytes": 1024,
      "status": "pending",
      "environment": "prod",
      "discovered_at": "2024-01-01T00:00:00Z",
      ...
    }
  ],
  "pagination": {
    "page": 0,
    "size": 50,
    "total": 100,
    "total_pages": 2
  }
}
```

### Get Discovery Details

```http
GET /api/discovery/1
```

**Response:**
```json
{
  "id": 1,
  "storage_location": {...},
  "file_metadata": {...},
  "schema_json": {...},
  "storage_metadata": {...},
  ...
}
```

### Approve Discovery

```http
PUT /api/discovery/1/approve
Content-Type: application/json

{
  "approved_by": "user@example.com",
  "role": "data_governor",
  "comments": "Approved for production use"
}
```

### Reject Discovery

```http
PUT /api/discovery/1/reject
Content-Type: application/json

{
  "rejected_by": "user@example.com",
  "rejection_reason": "Contains sensitive data",
  "role": "data_governor",
  "comments": "Needs encryption"
}
```

### Get Statistics

```http
GET /api/discovery/stats
```

**Response:**
```json
{
  "total": 1000,
  "pending": 50,
  "approved": 800,
  "rejected": 100,
  "by_environment": {
    "prod": 600,
    "dev": 400
  },
  "by_data_source": {
    "credit_card": 300,
    "pii": 200
  }
}
```

### Trigger Discovery

```http
POST /api/discovery/trigger
```

**Response:**
```json
{
  "message": "Discovery triggered successfully",
  "status": "running"
}
```

## Database Schema

The `data_discovery` table stores all discovered files with comprehensive metadata:

**Key Columns:**
- `id`: Primary key
- `storage_location`: JSON with storage path and connection info
- `file_metadata`: JSON with file name, size, hash, timestamps
- `schema_json`: JSON with extracted schema (columns, types)
- `schema_hash`: Hash of schema for change detection
- `status`: `pending`, `approved`, `rejected`, `published`, `archived`
- `approval_status`: `pending_review`, `approved`, `rejected`
- `environment`, `env_type`, `data_source_type`: Classification fields
- `discovered_at`, `last_checked_at`: Timestamps
- `discovery_info`: JSON with batch and source information

**Indexes:**
- Composite index on `storage_type`, `storage_identifier`, `storage_path` for deduplication
- Indexes on `status`, `environment`, `discovered_at` for filtering
- Full-text index on `file_name`, `folder_path` for search

See `database/migrations/data_discovery.sql` for the complete schema.

## Development

### Running Tests

```bash
# Backend tests (when available)
cd backend
pytest

# Frontend tests (when available)
cd frontend
npm test
```

### Code Style

- **Python**: Follow PEP 8, use type hints
- **JavaScript**: ESLint configuration included
- **SQL**: Use consistent naming conventions

### Adding New Storage Types

1. Create a new client in `airflow/utils/` (e.g., `s3_client.py`)
2. Update `azure_config.py` to support new storage type
3. Modify `azure_blob_discovery_dag.py` to handle new type
4. Update database schema if needed

### Adding New File Formats

1. Extend `metadata_extractor.py` to support new format
2. Add schema extraction logic
3. Update file sample retrieval in blob client

## Docker Deployment

### Production Deployment

1. **Build images:**
   ```bash
   docker-compose -f docker/docker-compose.yml build
   ```

2. **Set production environment variables:**
   - Use secrets management (Docker secrets, Kubernetes secrets, etc.)
   - Set strong passwords and keys
   - Configure production SMTP server

3. **Deploy:**
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

4. **Monitor logs:**
   ```bash
   docker-compose -f docker/docker-compose.yml logs -f
   ```

### Health Checks

- **Backend**: `GET http://localhost:5000/health`
- **Frontend**: Check if port 3000 is accessible
- **Airflow**: `GET http://localhost:8080/health`
- **MySQL**: `mysqladmin ping -h localhost`

## Troubleshooting

### Airflow DAG Not Running

1. Check if DAG is unpaused in Airflow UI
2. Verify DAG schedule interval
3. Check Airflow scheduler logs: `docker logs torro_airflow_scheduler`
4. Verify Azure connection string is set correctly

### Database Connection Errors

1. Check MySQL is running: `docker ps | grep mysql`
2. Verify connection credentials in `.env` files
3. Check connection pool settings
4. Review database logs: `docker logs torro_mysql`

### No Discoveries Found

1. Verify Azure storage connection string
2. Check container names and folder paths in configuration
3. Ensure files exist in specified locations
4. Check Airflow task logs for errors
5. Verify file extension filters (if set)

### Frontend Not Loading

1. Check backend API is accessible: `curl http://localhost:5000/health`
2. Verify CORS configuration in backend
3. Check browser console for errors
4. Verify `VITE_API_BASE_URL` in frontend environment

### Email Notifications Not Sending

1. Verify SMTP credentials in `airflow/.env`
2. Check SMTP server allows connections
3. Review email notifier logs
4. Test SMTP connection manually

### Performance Issues

1. **Large file counts:**
   - Adjust batch size in DAG (default: 100)
   - Increase database connection pool size
   - Consider partitioning by date

2. **Slow queries:**
   - Check database indexes are being used
   - Review query execution plans
   - Consider adding composite indexes

3. **Memory issues:**
   - Reduce batch size
   - Limit concurrent DAG runs (`max_active_runs=1`)
   - Increase container memory limits

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please [create an issue](link-to-issues) or contact the development team.
