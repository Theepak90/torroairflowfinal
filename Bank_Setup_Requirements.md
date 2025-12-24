# Bank Setup Requirements - Data Discovery Platform

This document outlines all the information and credentials that the bank needs to provide for setting up the Torro Data Discovery Platform.

---

## Table of Contents
1. [Azure Blob Storage Setup](#azure-blob-storage-setup)
2. [Oracle Database Setup](#oracle-database-setup)
3. [Email Notification Setup](#email-notification-setup)
4. [Optional: Azure AI Language Service (PII Detection)](#optional-azure-ai-language-service-pii-detection)

---

## Azure Blob Storage Setup

The platform scans Azure Blob Storage containers to discover data files. The bank needs to provide the following information:

### Required Information

#### 1. Storage Account Details
- **Storage Account Name**: `___________________________`
  - Example: `bankdatastorage`
  - This is the name of your Azure Storage Account

#### 2. Authentication Method
Choose one of the following authentication methods:

**Option A: Connection String (Simpler, less secure)**
- **Connection String**: `___________________________`
  - Can be found in: Azure Portal → Storage Account → Access Keys → Connection string
  - Format: `DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net`

**Option B: Service Principal (Recommended for production)**
- **Client ID (Application ID)**: `___________________________`
  - Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Client Secret**: `___________________________`
  - Secret value from Azure AD App Registration
- **Tenant ID**: `___________________________`
  - Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Required Azure Role**: Storage Blob Data Reader (minimum)
  - Must be assigned to the service principal on the storage account

#### 3. Container Configuration
- **Container Names**: `___________________________`
  - Comma-separated list (e.g., `container1,container2,container3`)
  - **OR** leave empty to scan ALL containers in the storage account
  - Example: `data-lake,raw-data,processed-data`

- **Folder Paths**: `___________________________`
  - Comma-separated list of folder paths to scan (e.g., `folder1,folder2/subfolder`)
  - **OR** leave empty to scan root of containers
  - Example: `transactions/2024,reports/monthly`

#### 4. Environment Classification
- **Environment Label**: `___________________________`
  - Examples: `prod`, `production`, `dev`, `development`, `test`
  - Used for filtering and organization

- **Environment Type**: `___________________________`
  - Options: `production` or `development`
  - Used for data classification

- **Data Source Type**: `___________________________`
  - Examples: `credit_card`, `transactions`, `customer_data`, `financial_reports`
  - Used for categorizing discovered data

#### 5. File Filtering (Optional)
- **File Extensions**: `___________________________`
  - Comma-separated list (e.g., `csv,json,parquet`)
  - **OR** leave empty to discover all file types
  - Example: `csv,parquet` (will only discover CSV and Parquet files)

---

## Oracle Database Setup

If the bank wants to use Oracle Database instead of MySQL for storing discovery metadata, provide the following:

### Required Information

#### 1. Database Connection Details
- **Host**: `___________________________`
  - Oracle database server hostname or IP address
  - Example: `oracle-db.bank.internal` or `192.168.1.100`

- **Port**: `___________________________`
  - Default: `1521`
  - Oracle listener port

- **Service Name or SID**: `___________________________`
  - Oracle service name (recommended) or SID
  - Example: `ORCL` or `bankdb.bank.internal`

- **Database Name**: `___________________________`
  - Name of the database/schema for discovery metadata
  - Example: `TORRO_DISCOVERY`

#### 2. Authentication
- **Username**: `___________________________`
  - Database user with appropriate permissions

- **Password**: `___________________________`
  - Database user password

#### 3. Required Permissions
The database user must have the following permissions:
- `CREATE TABLE`
- `CREATE INDEX`
- `INSERT`, `UPDATE`, `SELECT`, `DELETE` on discovery tables
- `CREATE SEQUENCE` (if using sequences for primary keys)

#### 4. Network Access
- **Firewall Rules**: Ensure the application server can connect to Oracle database
  - Port: `1521` (default) or custom port
  - Protocol: TCP

- **TNS Configuration** (if using TNS names):
  - Provide TNS entry name: `___________________________`
  - Or provide full TNS connection string

#### 5. SSL/TLS Configuration (Optional but Recommended)
- **SSL Mode**: `___________________________`
  - Options: `REQUIRED`, `PREFERRED`, `DISABLED`
  - Recommended: `REQUIRED` for production

- **SSL Certificate Path** (if using SSL): `___________________________`
  - Path to Oracle wallet or certificate files

---

## Email Notification Setup

The platform sends email notifications to data governors when new files are discovered.

### Required Information

- **SMTP Server**: `___________________________`
  - Example: `smtp.office365.com`, `smtp.gmail.com`, `mail.bank.internal`
  - Your organization's SMTP server address

- **SMTP Port**: `___________________________`
  - Common ports: `587` (TLS), `465` (SSL), `25` (unencrypted)
  - Recommended: `587` with TLS

- **SMTP Username**: `___________________________`
  - Email address or username for SMTP authentication
  - Example: `datagovernance@bank.com`

- **SMTP Password**: `___________________________`
  - Password or app-specific password for SMTP authentication
  - For Office 365/Gmail, may need app password if 2FA is enabled

- **Notification Recipients**: `___________________________`
  - Comma-separated list of email addresses
  - Example: `governor1@bank.com,governor2@bank.com,team@bank.com`
  - These are the data governors who will receive discovery notifications

- **Frontend URL** (for email links): `___________________________`
  - URL where the discovery dashboard is hosted
  - Example: `https://discovery.bank.com` or `https://internal.bank.com/discovery`

---

## Optional: Azure AI Language Service (PII Detection)

The platform can detect Personally Identifiable Information (PII) in column names using Azure AI Language Service.

### Required Information (Optional)

- **Azure AI Language Endpoint**: `___________________________`
  - Format: `https://<resource-name>.cognitiveservices.azure.com/`
  - Can be found in: Azure Portal → Cognitive Services → Language Service → Keys and Endpoint

- **Azure AI Language API Key**: `___________________________`
  - One of the two API keys from the Language Service resource
  - Can be found in: Azure Portal → Cognitive Services → Language Service → Keys and Endpoint

**Note**: If not provided, PII detection will be disabled and all columns will be marked as non-PII.

---

## Security Considerations

### For Azure Storage:
1. **Service Principal is recommended** over connection strings for production environments
2. Use **least privilege principle** - grant only `Storage Blob Data Reader` role
3. **Rotate credentials regularly** (especially service principal secrets)
4. **Enable audit logging** in Azure Storage Account

### For Oracle Database:
1. Use **dedicated database user** with minimal required permissions
2. **Enable SSL/TLS** for database connections in production
3. **Restrict network access** - only allow connections from application servers
4. **Use strong passwords** and rotate them regularly
5. **Enable database auditing** for discovery table access

### For Email:
1. Use **app-specific passwords** if 2FA is enabled
2. **Encrypt SMTP connections** (TLS/SSL)
3. **Limit notification recipients** to authorized data governors only
4. **Review email content** to ensure no sensitive data is included

---

## Delivery Format

Please provide the information in one of the following formats:

1. **Secure Document**: Encrypted PDF or password-protected document
2. **Secure File Transfer**: Via secure file sharing service (SharePoint, secure FTP, etc.)
3. **Direct Entry**: Bank IT team can directly configure in secure environment
4. **Encrypted Email**: PGP-encrypted email to authorized personnel

**Important**: Never send credentials via unencrypted email or chat.

---

## Checklist for Bank IT Team

- [ ] Azure Storage Account name provided
- [ ] Authentication method selected (Connection String or Service Principal)
- [ ] Authentication credentials provided (connection string OR service principal details)
- [ ] Service principal has Storage Blob Data Reader role assigned (if using service principal)
- [ ] Container names or "scan all" decision made
- [ ] Folder paths or "scan root" decision made
- [ ] Environment labels provided
- [ ] Data source type specified
- [ ] Oracle database connection details provided (if using Oracle)
- [ ] Oracle database user created with required permissions (if using Oracle)
- [ ] SMTP server details provided
- [ ] SMTP credentials provided
- [ ] Notification recipient email addresses provided
- [ ] Frontend URL provided
- [ ] Azure AI Language Service details provided (optional, for PII detection)
- [ ] All credentials delivered via secure channel

---

## Contact Information

For questions or clarifications regarding setup requirements, please contact:
- **Technical Contact**: [Your contact information]
- **Security Contact**: [Security team contact]

---

## Document Version

- **Version**: 1.0
- **Last Updated**: December 2024
- **Next Review**: [Date]

---

**Confidential - For Bank IT Team Use Only**

