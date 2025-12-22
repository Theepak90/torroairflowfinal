# Azure Service Principal Setup Guide

## Overview
This application now supports Azure Service Principal authentication for secure, read-only access to Azure Blob Storage. This is the recommended approach for production deployments.

## For IT Team - Creating Service Principal

### Prerequisites
- Azure CLI installed (`az --version`)
- Appropriate permissions to create service principals and assign roles
- Access to the Azure Storage Account

### Steps

1. **Login to Azure:**
   ```bash
   az login
   ```

2. **Set subscription (if you have multiple):**
   ```bash
   az account set --subscription <subscription-id>
   ```

3. **Get Storage Account Resource ID:**
   ```bash
   az storage account show --name <storage-account-name> --query id --output tsv
   ```
   Example output: `/subscriptions/xxx/resourceGroups/xxx/providers/Microsoft.Storage/storageAccounts/testfiletheepak`

4. **Create Service Principal with Read-Only Access:**
   ```bash
   az ad sp create-for-rbac --name "torro-data-discovery-readonly" \
     --role "Storage Blob Data Reader" \
     --scopes <storage-account-resource-id>
   ```

5. **Note the Output:**
   The command will return JSON with:
   - `appId` → Use as `AZURE_CLIENT_ID`
   - `password` → Use as `AZURE_CLIENT_SECRET`
   - `tenant` → Use as `AZURE_TENANT_ID`

   Example output:
   ```json
   {
     "appId": "12345678-1234-1234-1234-123456789abc",
     "password": "abc123~SecretPassword",
     "tenant": "87654321-4321-4321-4321-cba987654321"
   }
   ```

## For Deployment Team - Configuration

### Update .env File

Add the service principal credentials to `.env`:

```bash
# Azure Authentication Method
AZURE_AUTH_METHOD=service_principal

# Service Principal Credentials
AZURE_CLIENT_ID=<appId-from-step-5>
AZURE_CLIENT_SECRET=<password-from-step-5>
AZURE_TENANT_ID=<tenant-from-step-5>

# Storage Account Name (still required)
AZURE_STORAGE_ACCOUNT_NAME=<your-storage-account-name>
```

### Verify Configuration

1. **Test Service Principal Authentication:**
   ```bash
   cd airflow
   source venv/bin/activate
   python3 -c "
   import sys
   sys.path.insert(0, '.')
   from utils.azure_blob_client import AzureBlobClient
   from config.azure_config import AZURE_STORAGE_ACCOUNTS
   
   config = AZURE_STORAGE_ACCOUNTS[0]
   blob_client = AzureBlobClient(
       account_name=config['name'],
       client_id=config['client_id'],
       client_secret=config['client_secret'],
       tenant_id=config['tenant_id']
   )
   containers = blob_client.list_containers()
   print(f'✅ Success! Found {len(containers)} containers')
   "
   ```

2. **Test Discovery:**
   - Trigger manual discovery via frontend refresh button
   - Or wait for Airflow scheduled discovery (every 5 minutes)
   - Check that files are discovered successfully

## Security Notes

- **Read-Only Access:** The service principal has `Storage Blob Data Reader` role - it can only read, not modify or delete
- **Scope:** Access is scoped to the specific storage account
- **Credentials:** Store `AZURE_CLIENT_SECRET` securely - never commit to git
- **Rotation:** Service principal passwords can be rotated by IT team as needed

## Troubleshooting

### Error: "Authentication failed"
- Verify `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, and `AZURE_TENANT_ID` are correct
- Check that service principal has `Storage Blob Data Reader` role assigned
- Verify storage account name is correct

### Error: "Insufficient permissions"
- Ensure service principal has `Storage Blob Data Reader` role
- Check that role is assigned at storage account level (not subscription level)

### Fallback to Connection String
If service principal doesn't work, you can temporarily fall back to connection string:
```bash
AZURE_AUTH_METHOD=connection_string
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>
```

## Benefits of Service Principal

1. **Security:** No connection strings with full access keys
2. **Audit Trail:** All access is logged with service principal identity
3. **Least Privilege:** Read-only access only
4. **Easy Rotation:** Credentials can be rotated without changing connection strings
5. **Compliance:** Better for banking/enterprise security requirements

