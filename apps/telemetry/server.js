const express = require('express');
require('dotenv').config();

const TelemetryService = require('./main');
const healthRoutes = require('./routes/health');
const { errorHandler } = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 8083;

const telemetryService = new TelemetryService();

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

app.use('/health', healthRoutes);

app.use(errorHandler);

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🌡️ Telemetry Service running on port ${PORT}`);
  console.log(`📍 Available endpoints:`);
  console.log(`   GET /health - Health check`);
  console.log('🚀 Auto-starting telemetry service...');
  telemetryService.start();
});

module.exports = app;
