# Questions to Ask the Bank - Data Discovery Setup

## Storage Information (Already Have ✅)
- ✅ Storage Type: `azure_datalake`
- ✅ Account: `hblazlakehousepreprdstg1`
- ✅ Filesystem: `lh-enriched`
- ✅ Path: `visionplus/ATH3`

---

## 🔴 CRITICAL: Authentication Credentials (NEEDED)

### Question 1: Service Principal Credentials
**Ask**: "We need a Service Principal with read-only access to the Data Lake Storage. Please provide:"

1. **Azure AD Tenant ID**
   - Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - Where to find: Azure Portal → Azure Active Directory → Overview → Tenant ID

2. **Service Principal Client ID (Application ID)**
   - Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - This is the Application (client) ID of the Service Principal

3. **Service Principal Client Secret**
   - This is the secret/password for the Service Principal
   - **Important**: Ask if they can create a new secret or if they'll provide an existing one

### Question 2: Permissions/Role Assignment
**Ask**: "Please confirm the Service Principal has the following role:"

- **Role Name**: `Storage Blob Data Reader`
- **Scope**: Storage Account `hblazlakehousepreprdstg1`
- **OR**: Role assigned to filesystem `lh-enriched`

**Alternative Question**: "Can you assign the 'Storage Blob Data Reader' role to the Service Principal on storage account `hblazlakehousepreprdstg1`?"

---

## 📋 ADDITIONAL QUESTIONS

### Question 3: Access Scope
**Ask**: "Does the Service Principal have access to:"
- ✅ Storage Account: `hblazlakehousepreprdstg1`
- ✅ Filesystem: `lh-enriched`
- ✅ Path: `visionplus/ATH3`

**Follow-up**: "Are there any other paths/filesystems we need access to?"

### Question 4: Network/Firewall
**Ask**: "Are there any firewall rules or network restrictions we need to be aware of?"
- Do we need to whitelist any IP addresses?
- Is outbound HTTPS (443) access to Azure allowed from the VM?

### Question 5: Managed Identity (Alternative)
**Ask**: "If the application is hosted on an Azure VM, can we use Managed Identity instead of Service Principal?"
- This is more secure (no credentials to manage)
- They just need to assign the role to the VM's Managed Identity

### Question 6: Additional Paths
**Ask**: "Are there any other Data Lake paths we need to discover?"
- If yes, provide the ABFS paths in format: `abfs://filesystem@account.dfs.core.windows.net/path`

### Question 7: Environment Details
**Ask**: "What environment is this?"
- Production, Staging, Development?
- This helps with data classification

### Question 8: Data Classification
**Ask**: "What type of data is stored in `visionplus/ATH3`?"
- Helps with proper data classification (Internal, Restricted, Confidential)

---

## 📝 EMAIL TEMPLATE TO SEND TO BANK

```
Subject: Service Principal Credentials Required for Data Lake Storage Access

Dear IT Team,

We need Service Principal credentials to access the Data Lake Storage Gen2 for 
data discovery. Please provide the following:

1. Azure AD Tenant ID
2. Service Principal Client ID (Application ID)
3. Service Principal Client Secret

Storage Details:
- Storage Account: hblazlakehousepreprdstg1
- Filesystem: lh-enriched
- Path: visionplus/ATH3

Required Permissions:
- Role: "Storage Blob Data Reader"
- Scope: Storage Account "hblazlakehousepreprdstg1"

Purpose: Read-only access for automated data discovery and metadata extraction.

Alternative: If the application is hosted on an Azure VM, we can use Managed 
Identity instead (more secure, no credentials needed).

Please let us know:
1. Can you create a new Service Principal, or do you have an existing one?
2. What is the timeline for providing these credentials?
3. Are there any other paths/filesystems we need access to?

Thank you!
```

---

## ✅ CHECKLIST: What You Need from Bank

- [ ] Azure AD Tenant ID
- [ ] Service Principal Client ID
- [ ] Service Principal Client Secret
- [ ] Confirmation of "Storage Blob Data Reader" role assignment
- [ ] Confirmation of access to storage account `hblazlakehousepreprdstg1`
- [ ] Confirmation of access to filesystem `lh-enriched`
- [ ] Any additional paths/filesystems (if applicable)
- [ ] Network/firewall requirements (if any)
- [ ] Environment type (production/staging/dev)

---

## 🎯 SUMMARY: What to Ask

**Main Question**: 
"Please provide Service Principal credentials (Tenant ID, Client ID, Client Secret) with 'Storage Blob Data Reader' role on storage account `hblazlakehousepreprdstg1` for read-only data discovery access."

**Alternative**:
"If using Azure VM, can we use Managed Identity instead? Just assign 'Storage Blob Data Reader' role to the VM's Managed Identity."

