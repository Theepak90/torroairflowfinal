import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Pagination,
  Stack,
  CircularProgress,
  FormControl,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Visibility,
  CheckCircle,
  Cancel,
} from '@mui/icons-material';
import { STATUS_COLORS, STORAGE_TYPE_COLORS, PAGE_SIZES } from '../utils/constants';

const DiscoveryTable = ({
  discoveries,
  loading,
  pagination,
  onPageChange,
  onPageSizeChange,
  onViewDetails,
  onApprove,
  onReject,
}) => {
  const formatBytes = (bytes) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <Card sx={{ borderRadius: 0 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ borderRadius: 0 }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, fontFamily: 'Comfortaa' }}>
          Discoveries
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>File Name</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Storage Type</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Environment</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Data Source</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Size</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Discovered</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {discoveries && discoveries.length > 0 ? (
                discoveries.map((discovery) => (
                  <TableRow key={discovery.id}>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 500, fontFamily: 'Roboto' }}>
                        {discovery.file_name || (discovery.file_metadata?.basic?.name) || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={discovery.storage_type || 'azure_blob'}
                        size="small"
                        color={STORAGE_TYPE_COLORS[discovery.storage_type] || 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'Roboto' }}>
                        {discovery.environment || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'Roboto' }}>
                        {discovery.data_source_type || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'Roboto' }}>
                        {formatBytes(discovery.file_size_bytes)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'Roboto' }}>
                        {formatDate(discovery.discovered_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={discovery.status}
                        size="small"
                        color={STATUS_COLORS[discovery.status] || 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          startIcon={<Visibility />}
                          variant="outlined"
                          onClick={() => onViewDetails(discovery.id)}
                        >
                          View
                        </Button>
                        {discovery.status === 'pending' && (
                          <>
                            <Button
                              size="small"
                              startIcon={<CheckCircle />}
                              variant="contained"
                              color="success"
                              onClick={() => onApprove(discovery.id)}
                            >
                              Approve
                            </Button>
                            <Button
                              size="small"
                              startIcon={<Cancel />}
                              variant="contained"
                              color="error"
                              onClick={() => onReject(discovery.id)}
                            >
                              Reject
                            </Button>
                          </>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No discoveries found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {pagination && pagination.total > 0 && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Showing {discoveries.length} of {pagination.total} discoveries
              </Typography>
              <FormControl size="small" sx={{ minWidth: 80 }}>
                <Select value={pagination.size} onChange={(e) => onPageSizeChange(e.target.value)}>
                  {PAGE_SIZES.map((size) => (
                    <MenuItem key={size} value={size}>
                      {size}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Typography variant="body2" color="text.secondary">
                per page
              </Typography>
            </Box>

            <Pagination
              count={pagination.total_pages}
              page={pagination.page + 1}
              onChange={(event, page) => onPageChange(page - 1)}
              color="primary"
              showFirstButton
              showLastButton
              disabled={loading}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default DiscoveryTable;

