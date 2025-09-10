const express = require('express');

const router = express.Router();

// GET /health - Basic health check
router.get('/', (req, res) => {
  res.json({
    status: 'OK',
    service: 'DeviceManager',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

module.exports = router;
