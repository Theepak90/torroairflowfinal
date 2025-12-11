/**
 * Application Constants
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

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

