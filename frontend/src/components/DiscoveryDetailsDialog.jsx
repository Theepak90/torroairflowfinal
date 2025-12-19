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
              <Tab label="Technical" />
              <Tab label="Operational" />
              <Tab label="Business" />
              <Tab label="Schema & PII" />
            </Tabs>

            {/* Technical Metadata Tab */}
            {activeTab === 0 && (
              <Box>
                {(() => {
                  const techMeta = discovery.storage_data_metadata?.technical_metadata || {};
                  const fileSystem = techMeta.file_system || discovery.file_metadata?.basic || {};
                  const hash = techMeta.hash || discovery.file_metadata?.hash || {};
                  const timestamps = techMeta.timestamps || discovery.file_metadata?.timestamps || {};
                  const storage = techMeta.storage || discovery.storage_metadata?.azure || {};
                  const formatSpecific = techMeta.format_specific || {};
                  
                  const renderField = (label, value, isCode = false) => (
                    <Grid item xs={6} key={label}>
                  <Card variant="outlined">
                    <CardContent>
                          <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                            {label.toUpperCase()}
                          </Typography>
                          <Typography variant="body1" sx={{ wordBreak: 'break-word', fontFamily: isCode ? 'monospace' : 'inherit', fontSize: '0.875rem' }}>
                            {value || 'N/A'}
                          </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                  );
                  
                  return (
                    <Grid container spacing={2}>
                      {renderField('File Name', fileSystem.name)}
                      {renderField('Extension', fileSystem.extension)}
                      {renderField('Format', fileSystem.format)}
                      {renderField('Size', formatBytes(fileSystem.size_bytes))}
                      {renderField('MIME Type', fileSystem.mime_type)}
                      {renderField('Content Type', fileSystem.content_type)}
                      {renderField('Hash Algorithm', hash.algorithm, true)}
                      {renderField('Hash Value', hash.value, true)}
                      {renderField('Hash Computed At', formatDate(hash.computed_at))}
                      {renderField('Created At', formatDate(timestamps.created_at))}
                      {renderField('Last Modified', formatDate(timestamps.last_modified))}
                      {storage.type && renderField('Storage Type', storage.type)}
                      {storage.etag && storage.etag !== 'N/A' && renderField('ETag', storage.etag, true)}
                      {storage.access_tier && storage.access_tier !== 'N/A' && renderField('Access Tier', storage.access_tier)}
                      {storage.lease_status && storage.lease_status !== 'N/A' && renderField('Lease Status', storage.lease_status)}
                      {storage.content_encoding && storage.content_encoding !== 'N/A' && renderField('Content Encoding', storage.content_encoding)}
                      {storage.content_language && storage.content_language !== 'N/A' && renderField('Content Language', storage.content_language)}
                      {storage.cache_control && storage.cache_control !== 'N/A' && renderField('Cache Control', storage.cache_control)}
                      
                      {Object.keys(formatSpecific).length > 0 && (
                        <>
                          <Grid item xs={12} sx={{ mt: 2 }}>
                            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>Format Specific</Typography>
                          </Grid>
                          {Object.entries(formatSpecific).map(([key, value]) => (
                            <Grid item xs={12} key={key}>
                  <Card variant="outlined">
                    <CardContent>
                                  <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                                    {key.toUpperCase()}
                                  </Typography>
                                  <Typography variant="body1" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                                    {JSON.stringify(value, null, 2)}
                                  </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                          ))}
                        </>
                      )}
                    </Grid>
                  );
                })()}
              </Box>
            )}

            {/* Operational Metadata Tab */}
            {activeTab === 1 && (
              <Box>
                {(() => {
                  const opMeta = discovery.storage_data_metadata?.operational_metadata || {};
                  const discoveryInfo = opMeta.discovery || {};
                  const status = opMeta.status || {};
                  const workflow = opMeta.workflow || {};
                  
                  const renderField = (label, value) => (
                    <Grid item xs={6} key={label}>
                  <Card variant="outlined">
                    <CardContent>
                          <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                            {label.toUpperCase()}
                          </Typography>
                          <Typography variant="body1" sx={{ wordBreak: 'break-word', fontSize: '0.875rem' }}>
                            {value || 'N/A'}
                          </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                  );
                  
                  // Get actual values from discovery object
                  const discoveredAt = discoveryInfo.discovered_at || discovery.discovered_at;
                  const lastCheckedAt = discoveryInfo.last_checked_at || discovery.last_checked_at;
                  const batchId = discoveryInfo.discovery_batch_id || discovery.discovery_info?.batch?.id || discovery.discovery_info?.batch_id;
                  const schemaVersion = discoveryInfo.schema_version || discovery.schema_version || '1.0';
                  const schemaHash = discoveryInfo.schema_hash || discovery.schema_hash;
                  const currentStatus = status.current_status || discovery.status;
                  const approvalStatus = status.approval_status || discovery.approval_status;
                  const isVisible = status.is_visible !== undefined ? status.is_visible : discovery.is_visible;
                  const isActive = status.is_active !== undefined ? status.is_active : discovery.is_active;
                  const notificationSentAt = workflow.notification_sent_at || discovery.notification_sent_at;
                  const notificationRecipients = workflow.notification_recipients || discovery.notification_recipients;
                  
                  return (
                    <Grid container spacing={2}>
                      {renderField('Discovered At', formatDate(discoveredAt))}
                      {lastCheckedAt && renderField('Last Checked At', formatDate(lastCheckedAt))}
                      {batchId && renderField('Discovery Batch ID', batchId)}
                      {schemaVersion && renderField('Schema Version', schemaVersion)}
                      {schemaHash && (
                        <Grid item xs={12}>
                  <Card variant="outlined">
                    <CardContent>
                              <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                                SCHEMA HASH
                              </Typography>
                              <Typography variant="body1" sx={{ wordBreak: 'break-all', fontFamily: 'monospace', fontSize: '0.875rem' }}>
                                {schemaHash}
                              </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                      )}
                      {currentStatus && renderField('Current Status', currentStatus)}
                      {approvalStatus && renderField('Approval Status', approvalStatus)}
                      {notificationSentAt && renderField('Notification Sent At', formatDate(notificationSentAt))}
                      {notificationRecipients && Array.isArray(notificationRecipients) && notificationRecipients.length > 0 && renderField('Notification Recipients', notificationRecipients.join(', '))}
                      {notificationRecipients && !Array.isArray(notificationRecipients) && renderField('Notification Recipients', typeof notificationRecipients === 'string' ? notificationRecipients : JSON.stringify(notificationRecipients))}
                      {workflow.approval_workflow && (
                        <Grid item xs={12}>
                  <Card variant="outlined">
                    <CardContent>
                              <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                                APPROVAL WORKFLOW
                              </Typography>
                              <Typography variant="body1" sx={{ fontFamily: 'monospace', fontSize: '0.875rem', whiteSpace: 'pre-wrap' }}>
                                {JSON.stringify(workflow.approval_workflow || discovery.approval_workflow || {}, null, 2)}
                              </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                      )}
                    </Grid>
                  );
                })()}
              </Box>
            )}

            {/* Business Metadata Tab */}
            {activeTab === 2 && (
              <Box>
                {(() => {
                  const bizMeta = discovery.storage_data_metadata?.business_metadata || {};
                  const context = bizMeta.context || {};
                  const classification = bizMeta.classification || {};
                  const storageLocation = bizMeta.storage_location || {};
                  
                  const renderField = (label, value) => (
                    <Grid item xs={6} key={label}>
                  <Card variant="outlined">
                    <CardContent>
                          <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                            {label.toUpperCase()}
                          </Typography>
                          <Typography variant="body1" sx={{ wordBreak: 'break-word', fontSize: '0.875rem' }}>
                            {value || 'N/A'}
                          </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                  );
                  
                  // Get actual values from discovery object
                  const environment = context.environment || discovery.environment;
                  const envType = context.env_type || discovery.env_type;
                  const dataSourceType = context.data_source_type || discovery.data_source_type;
                  const folderPath = context.folder_path || discovery.folder_path;
                  const tags = classification.tags || discovery.tags;
                  // Data classification is auto-determined from PII detection
                  const dataClassification = classification.data_classification || 'Internal';
                  const sensitivityLevel = classification.sensitivity_level;
                  const container = storageLocation.container || discovery.storage_location?.container?.name;
                  const accountName = storageLocation.account_name || discovery.storage_location?.connection?.account_name;
                  const fullPath = storageLocation.full_path || discovery.storage_path || discovery.storage_location?.path;
                  
                  // Format tags for display
                  const formatTags = (tagsValue) => {
                    if (!tagsValue) return 'N/A';
                    if (Array.isArray(tagsValue) && tagsValue.length > 0) {
                      return tagsValue.join(', ');
                    }
                    if (typeof tagsValue === 'object') {
                      return JSON.stringify(tagsValue);
                    }
                    return String(tagsValue);
                  };
                  
                  return (
                    <Grid container spacing={2}>
                      {environment && renderField('Environment', environment)}
                      {/* Always show these fields */}
                      {renderField('Environment Type', envType || 'N/A')}
                      {renderField('Data Source Type', dataSourceType || 'N/A')}
                      {renderField('Tags', formatTags(tags))}
                      {renderField('Data Classification', dataClassification)}
                      {folderPath && renderField('Folder Path', folderPath)}
                      {sensitivityLevel && renderField('Sensitivity Level', sensitivityLevel)}
                      {container && renderField('Container', container)}
                      {accountName && renderField('Account Name', accountName)}
                      {fullPath && (
                        <Grid item xs={12}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                                FULL PATH
                              </Typography>
                              <Typography variant="body1" sx={{ wordBreak: 'break-all', fontFamily: 'monospace', fontSize: '0.875rem' }}>
                                {fullPath}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      )}
                    </Grid>
                  );
                })()}
              </Box>
            )}

            {/* Schema & PII Tab */}
            {activeTab === 3 && (
              <Box>
                {(() => {
                  const schemaPii = discovery.storage_data_metadata?.schema_pii || {};
                  const schema = schemaPii.schema || discovery.schema_json || {};
                  const piiSummary = schemaPii.pii_summary || {};
                  
                  if (!schema.columns || schema.columns.length === 0) {
                    return <Alert severity="info">No schema information available</Alert>;
                  }
                  
                  return (
                  <Box>
                      {piiSummary.total_columns > 0 && (
                        <Alert severity={piiSummary.pii_columns_count > 0 ? "warning" : "success"} sx={{ mb: 2 }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            Schema Summary: {piiSummary.total_columns} columns
                            {schema.num_rows !== null && schema.num_rows !== undefined && ` • ${schema.num_rows.toLocaleString()} rows`}
                            {schema.structure && ` • Structure: ${schema.structure}`}
                          </Typography>
                          {piiSummary.pii_columns_count > 0 && (
                            <Typography variant="body2" sx={{ mt: 1 }}>
                              ⚠️ PII Detected: {piiSummary.pii_columns_count} column(s) contain PII
                              {piiSummary.pii_types_found && piiSummary.pii_types_found.length > 0 && (
                                <> • Types: {piiSummary.pii_types_found.join(', ')}</>
                              )}
                            </Typography>
                          )}
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
                            {schema.columns.map((column, index) => (
                            <TableRow key={index}>
                              <TableCell sx={{ fontFamily: 'monospace' }}>{column.name}</TableCell>
                              <TableCell sx={{ fontFamily: 'monospace', color: 'primary.main' }}>{column.type}</TableCell>
                              <TableCell>{column.nullable ? 'Yes' : 'No'}</TableCell>
                              <TableCell>
                                {column.pii_detected ? (
                                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                    <Chip 
                                      label="PII Detected" 
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
                  );
                    })()}
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

