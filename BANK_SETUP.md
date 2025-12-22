# Bank Setup Guide - Data Discovery Platform

This guide provides step-by-step instructions for the bank's IT team to configure and deploy the Data Discovery Platform.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Azure Configuration](#azure-configuration)
3. [Service Principal Setup](#service-principal-setup)
4. [Environment Configuration](#environment-configuration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Infrastructure Requirements
- **VM/Server**: Single VM or server to host the application
- **Operating System**: Linux (Ubuntu 20.04+ or RHEL 8+)
- **Network**: Outbound HTTPS (443) access to Azure services
- **Ports**: 
  - Port 443 (HTTPS) - For Nginx reverse proxy
  - Port 3306 (MySQL) - Internal database access only

### Software Requirements
- **Python**: 3.11 (for Airflow) and 3.13 (for backend)
- **Node.js**: 20.x or higher
- **MySQL**: 8.0 or higher
- **Nginx**: Latest stable version

---

## Azure Configuration

### Storage Account Information

The bank needs to provide the following storage details:

#### For Azure Blob Storage:
- **Storage Account Name**: `your-storage-account-name`
- **Connection String** (optional, if using connection string auth)

#### For Azure Data Lake Storage Gen2:
- **Storage Account Name**: `hblazlakehousepreprdstg1`
- **Filesystem**: `lh-enriched`
- **Path**: `visionplus/ATH3`
- **Full ABFS Path**: `abfs://lh-enriched@hblazlakehousepreprdstg1.dfs.core.windows.net/visionplus/ATH3`

**Note**: Data Lake Storage Gen2 requires Service Principal authentication (connection strings are NOT supported).

---

## Service Principal Setup

### Option 1: Service Principal (Recommended for Service-to-Service Auth)

#### Step 1: Create Service Principal

The IT team needs to create a Service Principal with read-only access:

```bash
# Login to Azure CLI
az login

# Create Service Principal
az ad sp create-for-rbac \
  --name "torro-data-discovery-sp" \
  --role "Storage Blob Data Reader" \
  --scopes "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/hblazlakehousepreprdstg1"
```

**Output will contain:**
- `appId` → This is the **Client ID**
- `password` → This is the **Client Secret**
- `tenant` → This is the **Tenant ID**

#### Step 2: Grant Permissions

Ensure the Service Principal has the following role:

**Role**: `Storage Blob Data Reader`
**Scope**: Storage Account `hblazlakehousepreprdstg1`

Or assign at the filesystem level:
```bash
az role assignment create \
  --assignee <client-id> \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/hblazlakehousepreprdstg1/blobServices/default/containers/lh-enriched"
```

#### Step 3: Provide Credentials

Provide the following to the deployment team:

```
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
```

### Option 2: Managed Identity (Recommended for Azure VMs)

If the application is hosted on an Azure VM, use Managed Identity instead:

#### Step 1: Enable Managed Identity on VM

```bash
az vm identity assign \
  --name <vm-name> \
  --resource-group <resource-group>
```

#### Step 2: Grant Storage Access

```bash
az role assignment create \
  --assignee <managed-identity-principal-id> \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/hblazlakehousepreprdstg1"
```

**Note**: With Managed Identity, no credentials need to be provided. The code will automatically use the VM's Managed Identity.

---

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

#### Database Configuration
```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=<secure-password>
MYSQL_DATABASE=torro_discovery
MYSQL_DATABASE_AIRFLOW=airflow_metadata
```

#### Azure Storage Configuration

**For Blob Storage:**
```bash
AZURE_STORAGE_TYPE=blob
AZURE_STORAGE_ACCOUNT_NAME=<your-storage-account-name>
AZURE_STORAGE_CONNECTION_STRING=<connection-string>
AZURE_CONTAINERS=<comma-separated-container-names-or-empty-for-all>
AZURE_FOLDERS=<comma-separated-folder-paths-or-empty-for-root>
```

**For Data Lake Storage Gen2:**
```bash
AZURE_STORAGE_TYPE=datalake
AZURE_STORAGE_ACCOUNT_NAME=hblazlakehousepreprdstg1
AZURE_DATALAKE_PATHS=abfs://lh-enriched@hblazlakehousepreprdstg1.dfs.core.windows.net/visionplus/ATH3
AZURE_AUTH_METHOD=service_principal
AZURE_CLIENT_ID=<from-service-principal>
AZURE_CLIENT_SECRET=<from-service-principal>
AZURE_TENANT_ID=<from-service-principal>
```

**Note**: For Data Lake Storage, `AZURE_AUTH_METHOD` must be `service_principal`. Connection strings are not supported.

#### Application Configuration
```bash
AZURE_ENVIRONMENT=prod
AZURE_ENV_TYPE=production
AZURE_DATA_SOURCE_TYPE=credit_card

BACKEND_PORT=5001
AIRFLOW_WEBSERVER_PORT=8081

CORS_ORIGINS=https://<your-domain-or-ip>
```

#### Email Notification (Optional)
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<email-address>
SMTP_PASSWORD=<email-password>
NOTIFICATION_EMAILS=<comma-separated-email-addresses>
```

#### Azure AI Language Service - PII Detection (Optional)
```bash
AZURE_AI_LANGUAGE_ENDPOINT=https://<your-language-resource>.cognitiveservices.azure.com/
AZURE_AI_LANGUAGE_KEY=<your-ai-language-key>
```

---

## Setup Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd torroupdatedairflow
```

### 2. Install Dependencies

#### Backend (Python 3.13)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Airflow (Python 3.11)
```bash
cd airflow
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Frontend (Node.js 20+)
```bash
cd frontend
npm install
```

### 3. Configure Environment

Copy `.env` template and fill in values:
```bash
cp .env.example .env
# Edit .env with bank-specific values
```

### 4. Setup MySQL Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE torro_discovery CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE airflow_metadata CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Run migrations
USE torro_discovery;
SOURCE database/migrations/data_discovery.sql;
```

### 5. Initialize Airflow

```bash
cd airflow
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)

# Initialize database
airflow db migrate

# Create admin user
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@bank.com \
  --password <secure-password>
```

### 6. Start Services

#### Backend
```bash
cd backend
source venv/bin/activate
python app/main.py
```

#### Airflow Scheduler
```bash
cd airflow
source venv/bin/activate
airflow scheduler
```

#### Airflow Webserver
```bash
cd airflow
source venv/bin/activate
airflow webserver --port 8081
```

#### Frontend
```bash
cd frontend
npm run dev
```

#### Nginx (Reverse Proxy)
```bash
# Copy configuration
sudo cp nginx/torro-reverse-proxy.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/torro-reverse-proxy.conf /etc/nginx/sites-enabled/

# Generate SSL certificates (if needed)
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/key.pem \
  -out /etc/nginx/ssl/cert.pem

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

---

## Testing

### 1. Test Configuration

```bash
cd airflow
source venv/bin/activate
python3 -c "
from config.azure_config import AZURE_STORAGE_ACCOUNTS
config = AZURE_STORAGE_ACCOUNTS[0]
print('Storage Type:', config.get('storage_type'))
print('Account Name:', config.get('name'))
print('Auth Method:', config.get('auth_method'))
print('Has Credentials:', bool(config.get('client_id')))
"
```

### 2. Test Data Lake Connection

```bash
cd airflow
source venv/bin/activate
python3 -c "
from utils.azure_datalake_client import AzureDataLakeClient
from config.azure_config import AZURE_STORAGE_ACCOUNTS

config = AZURE_STORAGE_ACCOUNTS[0]
client = AzureDataLakeClient(
    account_name=config.get('name'),
    client_id=config.get('client_id'),
    client_secret=config.get('client_secret'),
    tenant_id=config.get('tenant_id')
)

filesystems = client.list_filesystems()
print(f'Found {len(filesystems)} filesystem(s)')
"
```

### 3. Test Discovery

#### Manual Discovery (via API)
```bash
curl -X POST https://<your-domain>/api/discovery/trigger
```

#### Automatic Discovery (via Airflow)
- Access Airflow UI: `https://<your-domain>/airflow`
- Navigate to DAGs
- Find `azure_blob_discovery` DAG
- Verify it's running (should run every 5 minutes automatically)

### 4. Verify Discoveries

```bash
curl https://<your-domain>/api/discovery?page=0&size=10
```

---

## Troubleshooting

### Authentication Errors

**Error**: `Authentication failed` or `Credential not configured`

**Solution**:
1. Verify Service Principal credentials are correct
2. Check Service Principal has `Storage Blob Data Reader` role
3. Verify role is assigned to correct storage account
4. Check Tenant ID matches the storage account's tenant

### Path Not Found Errors

**Error**: `Filesystem not found` or `Path does not exist`

**Solution**:
1. Verify filesystem name matches exactly: `lh-enriched`
2. Verify path exists: `visionplus/ATH3`
3. Check Service Principal has access to the filesystem
4. Verify storage account name is correct

### Connection Errors

**Error**: `Cannot connect to storage account`

**Solution**:
1. Verify network allows outbound HTTPS (443) to Azure
2. Check firewall rules
3. Verify storage account name is correct
4. Test connectivity: `curl https://hblazlakehousepreprdstg1.dfs.core.windows.net`

### Cross-Tenant Access Errors

**Error**: `Credential is not configured to acquire tokens for tenant`

**Solution**:
- The code already includes `additionally_allowed_tenants=["*"]` to allow cross-tenant access
- If still failing, verify Service Principal has access to the target tenant

---

## Security Considerations

1. **Credentials**: Store `.env` file securely, never commit to Git
2. **Permissions**: Use least privilege - `Storage Blob Data Reader` role only
3. **Network**: Restrict database access to localhost only
4. **SSL/TLS**: Use HTTPS (port 443) for all external access
5. **Service Principal**: Rotate secrets regularly (every 90 days recommended)

---

## Support

For issues or questions, contact the deployment team with:
- Error messages
- Logs from Airflow/Backend
- Configuration details (without sensitive credentials)

---

## Quick Reference

### Key Files
- `.env` - Environment configuration
- `airflow/dags/azure_blob_discovery_dag.py` - Discovery DAG
- `nginx/torro-reverse-proxy.conf` - Nginx configuration

### Key Endpoints
- Frontend: `https://<domain>/`
- Backend API: `https://<domain>/api/discovery`
- Airflow UI: `https://<domain>/airflow`
- Health Check: `https://<domain>/api/health`

### Discovery Schedule
- Automatic: Every 5 minutes (via Airflow DAG)
- Manual: POST to `/api/discovery/trigger`

---

**Last Updated**: December 2024

