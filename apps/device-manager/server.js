const express = require('express');
require('dotenv').config();

const deviceRoutes = require('./routes/devices');
const healthRoutes = require('./routes/health');
const { errorHandler } = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 8082;


// Basic middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/health', healthRoutes);
app.use('/api/v1/devices', deviceRoutes);

// Error handling middleware
app.use(errorHandler);


// Start server
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🏠 Device Management API server running on port ${PORT}`);
  console.log(`📍 Available endpoints:`);
  console.log(`   GET /health - Health check`);
  console.log(`   GET /api/v1/devices - Get all devices`);
  console.log(`   POST /api/v1/devices - Create new device`);
  console.log(`   GET /api/v1/devices/:id - Get device by ID`);
  console.log(`   PUT /api/v1/devices/:id - Update device`);
  console.log(`   DELETE /api/v1/devices/:id - Delete device`);
  console.log(`🔗 Monolith URL: ${process.env.MONOLITH_URL || 'http://localhost:8080'}`);
});

// Handle server errors
server.on('error', (error) => {
  console.error('Server error:', error);
  process.exit(1);
});

module.exports = app;
