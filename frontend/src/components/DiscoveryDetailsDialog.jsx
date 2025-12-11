import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Close,
} from '@mui/icons-material';

const DiscoveryDetailsDialog = ({ open, discovery, loading, onClose }) => {
  const [activeTab, setActiveTab] = React.useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      {loading ? (
        <Box sx={{ p: 4, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
          <CircularProgress />
          <Typography sx={{ mt: 2 }}>Loading discovery details...</Typography>
        </Box>
      ) : discovery ? (
        <>
          <DialogTitle>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  {discovery.file_name || (discovery.file_metadata?.basic?.name) || 'N/A'}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  <Chip label={discovery.status} size="small" color={discovery.status === 'approved' ? 'success' : discovery.status === 'rejected' ? 'error' : 'warning'} />
                  <Chip label={discovery.storage_type} size="small" variant="outlined" />
                </Box>
              </Box>
              <Button onClick={onClose} startIcon={<Close />}>
                Close
              </Button>
            </Box>
          </DialogTitle>
          <DialogContent dividers>
            <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
              <Tab label="Overview" />
              <Tab label="Schema" />
              <Tab label="Storage Metadata" />
            </Tabs>

            {/* Overview Tab */}
            {activeTab === 0 && (
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>File Name</Typography>
                      <Typography variant="body1">{discovery.file_name || (discovery.file_metadata?.basic?.name) || 'N/A'}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>File Format</Typography>
                      <Typography variant="body1">{discovery.file_metadata?.basic?.format || discovery.file_metadata?.basic?.extension || 'N/A'}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>File Size</Typography>
                      <Typography variant="body1">{formatBytes(discovery.file_size_bytes)}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>Environment</Typography>
                      <Typography variant="body1">{discovery.environment || 'N/A'}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>Data Source Type</Typography>
                      <Typography variant="body1">{discovery.data_source_type || 'N/A'}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>Discovered At</Typography>
                      <Typography variant="body1">{formatDate(discovery.discovered_at)}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>Storage Path</Typography>
                      <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                        {discovery.storage_path || (discovery.storage_location?.path) || 'N/A'}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}

            {/* Schema Tab */}
            {activeTab === 1 && (
              <Box>
                {discovery.schema_json && discovery.schema_json.columns && discovery.schema_json.columns.length > 0 ? (
                  <Box>
                    {discovery.schema_json.num_rows !== undefined && (
                      <Alert severity="info" sx={{ mb: 2 }}>
                        {discovery.schema_json.num_columns} columns
                        {discovery.schema_json.num_rows !== null && ` • ${discovery.schema_json.num_rows.toLocaleString()} rows`}
                        {discovery.schema_json.structure && ` • Structure: ${discovery.schema_json.structure}`}
                      </Alert>
                    )}
                    <TableContainer component={Paper} variant="outlined">
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell sx={{ fontWeight: 600 }}>Column Name</TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>Nullable</TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>PII Detection</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {discovery.schema_json.columns.map((column, index) => (
                            <TableRow key={index}>
                              <TableCell sx={{ fontFamily: 'monospace' }}>{column.name}</TableCell>
                              <TableCell sx={{ fontFamily: 'monospace', color: 'primary.main' }}>{column.type}</TableCell>
                              <TableCell>{column.nullable ? 'Yes' : 'No'}</TableCell>
                              <TableCell>
                                {column.pii_detected ? (
                                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                    <Chip 
                                      label="PII" 
                                      size="small" 
                                      color="error" 
                                      variant="filled"
                                      sx={{ fontWeight: 600 }}
                                    />
                                    {column.pii_types && column.pii_types.length > 0 && (
                                      column.pii_types.map((piiType, idx) => (
                                        <Chip
                                          key={idx}
                                          label={piiType}
                                          size="small"
                                          color="warning"
                                          variant="outlined"
                                        />
                                      ))
                                    )}
                                  </Box>
                                ) : (
                                  <Chip label="No PII" size="small" color="success" variant="outlined" />
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                ) : (
                  <Alert severity="info">No schema information available</Alert>
                )}
              </Box>
            )}

            {/* Storage Metadata Tab */}
            {activeTab === 2 && (
              <Box>
                {discovery.storage_metadata ? (
                  <Grid container spacing={2}>
                    {(() => {
                      // Handle both nested (azure: {...}) and flat structures
                      const metadata = discovery.storage_metadata.azure || discovery.storage_metadata;
                      
                      // Get file metadata for size and content type
                      const fileMetadata = discovery.file_metadata || {};
                      const basicInfo = fileMetadata.basic || {};
                      
                      // Define the fields to show in order
                      const fieldsToShow = [
                        { key: 'access_tier', label: 'Access Tier', value: metadata?.access_tier },
                        { key: 'creation_time', label: 'Creation Time', value: metadata?.creation_time || basicInfo.created_at || fileMetadata.timestamps?.created_at },
                        { key: 'type', label: 'Type', value: metadata?.type || 'Block blob' },
                        { key: 'size', label: 'Size', value: basicInfo.size_bytes ? formatBytes(basicInfo.size_bytes) : 'N/A' },
                        { key: 'content_type', label: 'Content Type', value: basicInfo.content_type || basicInfo.mime_type || metadata?.content_type },
                        { key: 'etag', label: 'ETag', value: metadata?.etag },
                        { key: 'last_modified', label: 'Last Modified', value: metadata?.last_modified || fileMetadata.timestamps?.last_modified },
                        { key: 'lease_status', label: 'Lease Status', value: metadata?.lease_status },
                      ];
                      
                      return fieldsToShow.map((field) => {
                        let displayValue = field.value;
                        
                        // Format dates
                        if (field.key === 'creation_time' || field.key === 'last_modified') {
                          if (displayValue) {
                            try {
                              const date = new Date(displayValue);
                              displayValue = date.toLocaleString('en-US', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit',
                                hour12: true
                              });
                            } catch (e) {
                              // Keep original if parsing fails
                            }
                          }
                        }
                        
                        // Handle null/undefined
                        if (displayValue === null || displayValue === undefined || displayValue === '') {
                          displayValue = 'N/A';
                        }
                        
                        // Handle objects (like metadata)
                        if (typeof displayValue === 'object' && !Array.isArray(displayValue)) {
                          const keys = Object.keys(displayValue);
                          if (keys.length === 0) {
                            displayValue = '-';
                          } else {
                            displayValue = JSON.stringify(displayValue, null, 2);
                          }
                        }
                        
                        return (
                          <Grid item xs={6} key={field.key}>
                            <Card variant="outlined">
                              <CardContent>
                                <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                                  {field.label.toUpperCase()}
                                </Typography>
                                <Typography variant="body1" sx={{ wordBreak: 'break-word', fontFamily: 'monospace', fontSize: '0.875rem' }}>
                                  {String(displayValue)}
                                </Typography>
                              </CardContent>
                            </Card>
                          </Grid>
                        );
                      });
                    })()}
                  </Grid>
                ) : (
                  <Alert severity="info">No storage metadata available</Alert>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={onClose} variant="outlined">
              Close
            </Button>
          </DialogActions>
        </>
      ) : null}
    </Dialog>
  );
};

export default DiscoveryDetailsDialog;

