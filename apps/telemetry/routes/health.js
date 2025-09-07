const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    status: 'OK',
    service: 'TelemetryService',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

module.exports = router;
