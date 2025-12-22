# Bank Required Configuration Checklist

This document lists **ALL** configuration values the bank's IT team needs to provide for the Data Discovery Platform to work.

---

## 🔴 CRITICAL: Must Fill (Required for System to Work)

### 1. Database Configuration
```bash
MYSQL_HOST=localhost                    # Database server (usually localhost)
MYSQL_PORT=3306                         # Database port (usually 3306)
MYSQL_USER=root                         # Database username
MYSQL_PASSWORD=<BANK_MUST_PROVIDE>      # Database password (secure password)
MYSQL_DATABASE=torro_discovery          # Main database name
MYSQL_DATABASE_AIRFLOW=airflow_metadata # Airflow metadata database name
```

**Bank Must Provide**: `MYSQL_PASSWORD`

---

### 2. Azure Data Lake Storage Authentication (REQUIRED)

#### Option A: Service Principal (Required for Data Lake)
```bash
AZURE_STORAGE_TYPE=datalake
AZURE_STORAGE_ACCOUNT_NAME=hblazlakehousepreprdstg1
AZURE_DATALAKE_PATHS=abfs://lh-enriched@hblazlakehousepreprdstg1.dfs.core.windows.net/visionplus/ATH3
AZURE_AUTH_METHOD=service_principal

AZURE_TENANT_ID=<BANK_MUST_PROVIDE>           # Azure AD Tenant ID
AZURE_CLIENT_ID=<BANK_MUST_PROVIDE>            # Service Principal Client ID
AZURE_CLIENT_SECRET=<BANK_MUST_PROVIDE>        # Service Principal Client Secret
```

**Bank Must Provide**:
- ✅ `AZURE_TENANT_ID`
- ✅ `AZURE_CLIENT_ID`
- ✅ `AZURE_CLIENT_SECRET`

**Note**: Data Lake Storage Gen2 **DOES NOT** support connection strings. Service Principal is **REQUIRED**.

#### Option B: Managed Identity (If Azure VM)
```bash
AZURE_STORAGE_TYPE=datalake
AZURE_STORAGE_ACCOUNT_NAME=hblazlakehousepreprdstg1
AZURE_DATALAKE_PATHS=abfs://lh-enriched@hblazlakehousepreprdstg1.dfs.core.windows.net/visionplus/ATH3
AZURE_AUTH_METHOD=managed_identity
```

**Bank Must Do**: Assign "Storage Blob Data Reader" role to VM's Managed Identity (no credentials needed)

---

### 3. Application URLs (For CORS and Notifications)
```bash
CORS_ORIGINS=https://<BANK_DOMAIN_OR_IP>      # Frontend URL (e.g., https://192.168.1.15 or https://data-discovery.bank.com)
```

**Bank Must Provide**: `CORS_ORIGINS` (the URL where frontend will be accessed)

---

### 4. Airflow Configuration (REQUIRED)

#### 4a. Airflow Database Connection
The `airflow/airflow.cfg` file contains a hardcoded database connection string. The bank must update it with their MySQL password:

**File**: `airflow/airflow.cfg` (line 55)
```ini
sql_alchemy_conn = mysql+pymysql://root:<BANK_MYSQL_PASSWORD>@localhost:3306/airflow_metadata?charset=utf8mb4
```

**Bank Must Do**: Replace `<BANK_MYSQL_PASSWORD>` with their actual MySQL password.

#### 4b. Airflow Admin User
An Airflow admin user must be created during setup. The bank needs to provide:

```bash
# Command to create admin user (run during setup):
airflow users create \
  --username <BANK_AIRFLOW_USERNAME> \
  --firstname <FIRSTNAME> \
  --lastname <LASTNAME> \
  --role Admin \
  --email <BANK_EMAIL> \
  --password <BANK_AIRFLOW_PASSWORD>
```

**Bank Must Provide**:
- ✅ `AIRFLOW_ADMIN_USERNAME` - Username for Airflow admin (e.g., `admin`)
- ✅ `AIRFLOW_ADMIN_PASSWORD` - Password for Airflow admin (secure password)
- ✅ `AIRFLOW_ADMIN_EMAIL` - Email address for Airflow admin

**Note**: This is a one-time setup step. The admin user is used to log into the Airflow UI.

#### 4c. Airflow Fernet Key (Optional)
```bash
AIRFLOW_FERNET_KEY=<BANK_FERNET_KEY>    # Optional: Airflow encryption key
```

**Bank Must Provide** (optional):
- `AIRFLOW_FERNET_KEY` - If not provided, Airflow will generate one automatically

**Note**: If the bank wants to use a custom Fernet key for encryption, they can generate one with:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🟡 OPTIONAL: Recommended to Fill

### 5. Email Notifications (Optional but Recommended)
```bash
SMTP_SERVER=smtp.gmail.com                    # SMTP server (or bank's SMTP server)
SMTP_PORT=587                                 # SMTP port (usually 587 or 465)
SMTP_USER=<BANK_EMAIL>                        # SMTP username/email
SMTP_PASSWORD=<BANK_EMAIL_PASSWORD>           # SMTP password
NOTIFICATION_EMAILS=<EMAIL1>,<EMAIL2>         # Comma-separated email addresses for notifications
```

**Bank Must Provide** (if they want email notifications):
- `SMTP_SERVER` (if not using Gmail)
- `SMTP_USER`
- `SMTP_PASSWORD`
- `NOTIFICATION_EMAILS`

---

### 6. Azure AI Language Service - PII Detection (Optional)
```bash
AZURE_AI_LANGUAGE_ENDPOINT=https://<BANK_LANGUAGE_RESOURCE>.cognitiveservices.azure.com/
AZURE_AI_LANGUAGE_KEY=<BANK_AI_LANGUAGE_KEY>
```

**Bank Must Provide** (if they want Azure DLP for PII detection):
- `AZURE_AI_LANGUAGE_ENDPOINT`
- `AZURE_AI_LANGUAGE_KEY`

**Note**: If not provided, system will use pattern-based PII detection as fallback.

---

### 7. Environment Classification (Optional but Recommended)
```bash
AZURE_ENVIRONMENT=prod                        # Environment: prod, staging, dev
AZURE_ENV_TYPE=production                     # Environment type: production, staging, development
AZURE_DATA_SOURCE_TYPE=credit_card            # Data source type: credit_card, banking, etc.
```

**Bank Must Provide** (recommended for proper data classification):
- `AZURE_ENVIRONMENT`
- `AZURE_ENV_TYPE`
- `AZURE_DATA_SOURCE_TYPE`

---

## 📋 COMPLETE CHECKLIST FOR BANK

### ✅ Must Fill (System Won't Work Without These)

- [ ] **MYSQL_PASSWORD** - Database password
- [ ] **AZURE_TENANT_ID** - Azure AD Tenant ID
- [ ] **AZURE_CLIENT_ID** - Service Principal Client ID
- [ ] **AZURE_CLIENT_SECRET** - Service Principal Client Secret
- [ ] **CORS_ORIGINS** - Frontend URL (e.g., `https://192.168.1.15` or `https://data-discovery.bank.com`)
- [ ] **Update `airflow/airflow.cfg`** - Replace MySQL password in database connection string (line 55)
- [ ] **AIRFLOW_ADMIN_USERNAME** - Username for Airflow admin user
- [ ] **AIRFLOW_ADMIN_PASSWORD** - Password for Airflow admin user
- [ ] **AIRFLOW_ADMIN_EMAIL** - Email address for Airflow admin user

### ⚠️ Recommended (System Works But Limited Without These)

- [ ] **SMTP_SERVER** - Email server (if notifications needed)
- [ ] **SMTP_USER** - Email username (if notifications needed)
- [ ] **SMTP_PASSWORD** - Email password (if notifications needed)
- [ ] **NOTIFICATION_EMAILS** - Email addresses for notifications
- [ ] **AZURE_AI_LANGUAGE_ENDPOINT** - Azure DLP endpoint (for better PII detection)
- [ ] **AZURE_AI_LANGUAGE_KEY** - Azure DLP key (for better PII detection)
- [ ] **AZURE_ENVIRONMENT** - Environment type (prod/staging/dev)
- [ ] **AZURE_ENV_TYPE** - Environment classification
- [ ] **AZURE_DATA_SOURCE_TYPE** - Type of data being discovered
- [ ] **AIRFLOW_FERNET_KEY** - Custom encryption key (optional, Airflow can generate automatically)

---

## 📝 MINIMUM CONFIGURATION (System Will Work)

If bank only provides the **minimum required**, system will work with:

```bash
# Database
MYSQL_PASSWORD=<secure-password>

# Azure Data Lake Storage
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>

# Application URL
CORS_ORIGINS=https://<bank-domain-or-ip>

# Airflow Configuration
# 1. Update airflow/airflow.cfg (line 55) with MySQL password
# 2. Create Airflow admin user:
#    - AIRFLOW_ADMIN_USERNAME (e.g., "admin")
#    - AIRFLOW_ADMIN_PASSWORD (secure password)
#    - AIRFLOW_ADMIN_EMAIL (e.g., "admin@bank.com")
```

**Everything else has defaults or is optional.**

---

## 🔧 ALREADY CONFIGURED (No Action Needed)

These are already set and don't need to be changed:

```bash
# Database (defaults)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_DATABASE=torro_discovery
MYSQL_DATABASE_AIRFLOW=airflow_metadata

# Azure Storage (already configured)
AZURE_STORAGE_TYPE=datalake
AZURE_STORAGE_ACCOUNT_NAME=hblazlakehousepreprdstg1
AZURE_DATALAKE_PATHS=abfs://lh-enriched@hblazlakehousepreprdstg1.dfs.core.windows.net/visionplus/ATH3
AZURE_AUTH_METHOD=service_principal

# Application Ports (defaults)
BACKEND_PORT=5001
AIRFLOW_WEBSERVER_PORT=8081

# Database Pool (defaults)
DB_POOL_MIN=5
DB_POOL_MAX=20
DB_POOL_RECYCLE=3600
```

---

## 📧 QUICK REFERENCE: What Bank Needs to Provide

### Critical (9 items):
1. **MYSQL_PASSWORD** - Database password
2. **AZURE_TENANT_ID** - Azure AD Tenant ID
3. **AZURE_CLIENT_ID** - Service Principal Client ID
4. **AZURE_CLIENT_SECRET** - Service Principal Client Secret
5. **CORS_ORIGINS** - Frontend URL
6. **Update `airflow/airflow.cfg`** - Replace MySQL password in database connection string
7. **AIRFLOW_ADMIN_USERNAME** - Airflow admin username
8. **AIRFLOW_ADMIN_PASSWORD** - Airflow admin password
9. **AIRFLOW_ADMIN_EMAIL** - Airflow admin email

### Optional (8 items):
10. SMTP credentials (if email notifications needed)
11. Azure AI Language Service credentials (if better PII detection needed)
12. Environment classification details
13. AIRFLOW_FERNET_KEY (optional, Airflow can generate automatically)

---

## 🎯 SUMMARY FOR BANK IT TEAM

**Minimum Required** (9 items):
- Database password (1)
- Service Principal credentials (3: Tenant ID, Client ID, Client Secret)
- Frontend URL (1)
- Airflow configuration (4: Update airflow.cfg, Admin username, Admin password, Admin email)

**Total**: 9 critical items + 8 optional items = **17 possible items**

**System will work with just the 9 critical items.**

---

## 📌 IMPORTANT AIRFLOW SETUP NOTES

1. **`airflow/airflow.cfg` must be edited manually** - The database connection string contains a hardcoded password that must be updated with the bank's MySQL password.

2. **Airflow admin user is created via command** - This is a one-time setup step during installation. The bank must provide username, password, and email for the admin user.

3. **Airflow Fernet Key** - If not provided, Airflow will automatically generate one. Only needed if the bank wants to use a custom encryption key.

