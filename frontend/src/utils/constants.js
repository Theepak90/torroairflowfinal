/**
 * Application Constants
 */

// API base URL - uses environment variable or relative path for nginx proxy
const getApiBaseUrl = () => {
  // If explicitly set via environment variable, use it
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  // Use relative path - nginx will proxy /api to backend
  // Relative paths work correctly when accessed through Nginx
  // IMPORTANT: Access frontend via HTTPS (https://127.0.0.1/airflow-fe/)
  // to avoid HTTP->HTTPS redirect issues with fetch()
  return '/api';
};

export const API_BASE_URL = getApiBaseUrl();

export const STATUS_COLORS = {
  pending: 'warning',
  approved: 'success',
  rejected: 'error',
  published: 'info',
  archived: 'default',
};

export const STORAGE_TYPE_COLORS = {
  azure_blob: 'secondary',
  aws_s3: 'warning',
  gcs: 'primary',
};

export const PAGE_SIZES = [25, 50, 100];

