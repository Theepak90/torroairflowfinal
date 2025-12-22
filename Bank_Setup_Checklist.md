# Bank Setup Checklist - Quick Reference

## Azure Blob Storage Configuration

| Item | Value | Notes |
|------|-------|-------|
| Storage Account Name | | |
| Authentication Method | ☐ Connection String<br>☐ Service Principal | |
| Connection String | | (If using Connection String) |
| Client ID | | (If using Service Principal) |
| Client Secret | | (If using Service Principal) |
| Tenant ID | | (If using Service Principal) |
| Container Names | | (Comma-separated, or leave empty for all) |
| Folder Paths | | (Comma-separated, or leave empty for root) |
| Environment Label | | (e.g., prod, dev) |
| Environment Type | ☐ Production<br>☐ Development | |
| Data Source Type | | (e.g., credit_card, transactions) |
| File Extensions | | (Optional, comma-separated) |

---

## Oracle Database Configuration

| Item | Value | Notes |
|------|-------|-------|
| Database Host | | |
| Database Port | | (Default: 1521) |
| Service Name/SID | | |
| Database Name | | |
| Username | | |
| Password | | |
| SSL Mode | ☐ Required<br>☐ Preferred<br>☐ Disabled | |
| TNS Name | | (If using TNS) |

---

## Email Notification Configuration

| Item | Value | Notes |
|------|-------|-------|
| SMTP Server | | |
| SMTP Port | | (Common: 587, 465, 25) |
| SMTP Username | | |
| SMTP Password | | |
| Notification Recipients | | (Comma-separated emails) |
| Frontend URL | | (For email links) |

---

## Optional: Azure AI Language Service (PII Detection)

| Item | Value | Notes |
|------|-------|-------|
| AI Language Endpoint | | (Optional) |
| AI Language API Key | | (Optional) |

---

## Security Checklist

- [ ] All credentials provided via secure channel
- [ ] Service Principal has Storage Blob Data Reader role (if using SP)
- [ ] Oracle database user has minimal required permissions
- [ ] SSL/TLS enabled for database connections
- [ ] Firewall rules configured for database access
- [ ] SMTP uses encrypted connection (TLS/SSL)
- [ ] Notification recipients are authorized data governors

---

**Completed By**: _________________  
**Date**: _________________  
**Approved By**: _________________  
**Date**: _________________

