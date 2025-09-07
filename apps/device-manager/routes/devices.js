const express = require('express');
const deviceService = require('../main');
const { validateDevice, validateDeviceUpdate } = require('../middleware/validation');

const router = express.Router();

// GET /api/v1/devices - Get all devices
router.get('/', async (req, res, next) => {
  try {
    const devices = await deviceService.getAllDevices();

    res.json({
      success: true,
      data: devices,
      count: devices.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(error);
  }
});

// GET /api/v1/devices/:id - Get device by ID
router.get('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;

    // Validate ID parameter
    if (!id || id.trim() === '') {
      return res.status(400).json({
        success: false,
        error: 'Device ID is required',
        timestamp: new Date().toISOString()
      });
    }

    const device = await deviceService.getDeviceById(id);

    if (!device) {
      return res.status(404).json({
        success: false,
        error: 'Device not found',
        timestamp: new Date().toISOString()
      });
    }

    res.json({
      success: true,
      data: device,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(error);
  }
});

// POST /api/v1/devices - Create new device
router.post('/', validateDevice, async (req, res, next) => {
  try {
    const deviceData = req.body;
    const device = await deviceService.createDevice(deviceData);

    res.status(201).json({
      success: true,
      data: device,
      message: 'Device created successfully',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(error);
  }
});

// PUT /api/v1/devices/:id - Update device
router.put('/:id', validateDeviceUpdate, async (req, res, next) => {
  try {
    const { id } = req.params;
    console.log(`🔄 PUT /api/v1/devices/${id} - Received request`);
    console.log(`📝 Request body:`, JSON.stringify(req.body, null, 2));

    // Validate ID parameter
    if (!id || id.trim() === '') {
      return res.status(400).json({
        success: false,
        error: 'Device ID is required',
        timestamp: new Date().toISOString()
      });
    }

    const updateData = req.body;
    console.log(`🚀 Calling deviceService.updateDevice with:`, JSON.stringify(updateData, null, 2));

    const device = await deviceService.updateDevice(id, updateData);

    res.json({
      success: true,
      data: device,
      message: 'Device updated successfully',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(error);
  }
});

// DELETE /api/v1/devices/:id - Delete device
router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;

    // Validate ID parameter
    if (!id || id.trim() === '') {
      return res.status(400).json({
        success: false,
        error: 'Device ID is required',
        timestamp: new Date().toISOString()
      });
    }

    await deviceService.deleteDevice(id);

    res.json({
      success: true,
      message: 'Device deleted successfully',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
