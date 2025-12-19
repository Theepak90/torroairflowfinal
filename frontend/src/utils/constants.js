/**
 * Application Constants
 */

// API base URL - uses environment variable or relative path for nginx proxy
const getApiBaseUrl = () => {
  // If explicitly set via environment variable, use it
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  // Default to relative path - nginx will proxy /api to backend
  // This works with HTTPS on port 443 via nginx reverse proxy
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

