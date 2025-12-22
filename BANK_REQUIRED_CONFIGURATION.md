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

## 🟡 OPTIONAL: Recommended to Fill

### 4. Email Notifications (Optional but Recommended)
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

### 5. Azure AI Language Service - PII Detection (Optional)
```bash
AZURE_AI_LANGUAGE_ENDPOINT=https://<BANK_LANGUAGE_RESOURCE>.cognitiveservices.azure.com/
AZURE_AI_LANGUAGE_KEY=<BANK_AI_LANGUAGE_KEY>
```

**Bank Must Provide** (if they want Azure DLP for PII detection):
- `AZURE_AI_LANGUAGE_ENDPOINT`
- `AZURE_AI_LANGUAGE_KEY`

**Note**: If not provided, system will use pattern-based PII detection as fallback.

---

### 6. Environment Classification (Optional but Recommended)
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

### Critical (5 items):
1. **MYSQL_PASSWORD** - Database password
2. **AZURE_TENANT_ID** - Azure AD Tenant ID
3. **AZURE_CLIENT_ID** - Service Principal Client ID
4. **AZURE_CLIENT_SECRET** - Service Principal Client Secret
5. **CORS_ORIGINS** - Frontend URL

### Optional (7 items):
6. SMTP credentials (if email notifications needed)
7. Azure AI Language Service credentials (if better PII detection needed)
8. Environment classification details

---

## 🎯 SUMMARY FOR BANK IT TEAM

**Minimum Required** (5 values):
- Database password
- Service Principal credentials (3 values: Tenant ID, Client ID, Client Secret)
- Frontend URL

**Total**: 5 critical values + 7 optional values = **12 possible values**

**System will work with just the 5 critical values.**

