import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
} from '@mui/material';
import {
  DataObject,
  PendingActions,
  CheckCircle,
  Cancel,
} from '@mui/icons-material';

const SummaryCards = ({ stats }) => {
  const cards = [
    {
      title: 'Total Discoveries',
      value: stats?.total_discoveries || 0,
      icon: <DataObject sx={{ fontSize: 24, color: 'primary.main' }} />,
      color: 'primary',
    },
    {
      title: 'Pending Approvals',
      value: stats?.pending_count || 0,
      icon: <PendingActions sx={{ fontSize: 24, color: 'warning.main' }} />,
      color: 'warning',
    },
    {
      title: 'Approved',
      value: stats?.approved_count || 0,
      icon: <CheckCircle sx={{ fontSize: 24, color: 'success.main' }} />,
      color: 'success',
    },
    {
      title: 'Rejected',
      value: stats?.rejected_count || 0,
      icon: <Cancel sx={{ fontSize: 24, color: 'error.main' }} />,
      color: 'error',
    },
  ];

  return (
    <Box sx={{ p: 3, pb: 2 }}>
      <Grid container spacing={3}>
        {cards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              elevation={1}
              sx={{
                height: '140px',
                borderRadius: 0,
                display: 'flex',
                flexDirection: 'column',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px 0 rgba(0, 0, 0, 0.15)',
                },
              }}
            >
              <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {card.icon}
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1, fontWeight: 500 }}>
                    {card.title}
                  </Typography>
                </Box>
                <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 0.5, fontSize: '1.75rem' }}>
                    {card.value}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default SummaryCards;

