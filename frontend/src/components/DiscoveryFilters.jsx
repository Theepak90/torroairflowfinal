import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  InputAdornment,
} from '@mui/material';
import {
  Search,
  FilterList,
} from '@mui/icons-material';

const DiscoveryFilters = ({
  searchTerm,
  onSearchChange,
  statusFilter,
  onStatusChange,
  environmentFilter,
  onEnvironmentChange,
  dataSourceFilter,
  onDataSourceChange,
  onClearFilters,
}) => {
  return (
    <Card sx={{ mb: 3, borderRadius: 0 }}>
      <CardContent>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search discoveries..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                label="Status"
                onChange={(e) => onStatusChange(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="approved">Approved</MenuItem>
                <MenuItem value="rejected">Rejected</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Environment</InputLabel>
              <Select
                value={environmentFilter}
                label="Environment"
                onChange={(e) => onEnvironmentChange(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="dev">Dev</MenuItem>
                <MenuItem value="staging">Staging</MenuItem>
                <MenuItem value="prod">Prod</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Data Source</InputLabel>
              <Select
                value={dataSourceFilter}
                label="Data Source"
                onChange={(e) => onDataSourceChange(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="credit_card">Credit Card</MenuItem>
                <MenuItem value="transactions">Transactions</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterList />}
              onClick={onClearFilters}
            >
              Clear
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default DiscoveryFilters;

