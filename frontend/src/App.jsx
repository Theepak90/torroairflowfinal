import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import DataDiscoveryPage from './pages/DataDiscoveryPage';
import './index.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#5C6BB5',
    },
    secondary: {
      main: '#8FA0F5',
    },
    background: {
      default: '#fafafa',
    },
  },
  typography: {
    fontFamily: "'Roboto', system-ui, Avenir, Helvetica, Arial, sans-serif",
    h1: {
      fontFamily: "'Comfortaa', cursive",
      fontWeight: 600,
    },
    h2: {
      fontFamily: "'Comfortaa', cursive",
      fontWeight: 600,
    },
    h3: {
      fontFamily: "'Comfortaa', cursive",
      fontWeight: 600,
    },
    h4: {
      fontFamily: "'Comfortaa', cursive",
      fontWeight: 600,
    },
    h5: {
      fontFamily: "'Comfortaa', cursive",
      fontWeight: 600,
    },
    h6: {
      fontFamily: "'Comfortaa', cursive",
      fontWeight: 600,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router basename="/airflow-fe">
        <Routes>
          <Route path="/" element={<DataDiscoveryPage />} />
          <Route path="/discovery" element={<DataDiscoveryPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;

