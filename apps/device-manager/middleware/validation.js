const isString = (value) => typeof value === 'string';
const isNonEmptyString = (value) => isString(value) && value.trim().length > 0;
const isValidDeviceType = (type) => ['temperature', 'humidity', 'motion', 'thermostat'].includes(type);

const validationError = (res, errors) => {
  return res.status(400).json({
    success: false,
    error: 'Validation error',
    details: errors,
    timestamp: new Date().toISOString()
  });
};

const validateDevice = (req, res, next) => {
  const { device_name, device_type, home_id, location, configuration } = req.body;
  const errors = [];

  if (!device_name) {
    errors.push('device_name is required');
  } else if (!isNonEmptyString(device_name)) {
    errors.push('device_name must be a non-empty string');
  }

  if (!device_type) {
    errors.push('device_type is required');
  } else if (!isValidDeviceType(device_type)) {
    errors.push('device_type must be one of: temperature, humidity, motion, thermostat');
  }

  if (location !== undefined && !isNonEmptyString(location)) {
    errors.push('location must be a non-empty string');
  }

  if (configuration !== undefined && typeof configuration !== 'object') {
    errors.push('configuration must be an object');
  }

  if (errors.length > 0) {
    return validationError(res, errors);
  }

  req.body = {
    device_name: device_name.trim(),
    device_type: device_type,
    home_id,
    location: location ? location.trim() : undefined,
    configuration: configuration
  };

  next();
};

const validateDeviceUpdate = (req, res, next) => {
  const { device_name, device_type, home_id, location, configuration } = req.body;
  const errors = [];
  const hasFields = device_name || device_type || home_id || location || configuration;

  if (!hasFields) {
    errors.push('At least one field must be provided for update');
  }

  if (device_name !== undefined) {
    if (!isNonEmptyString(device_name)) {
      errors.push('device_name must be a non-empty string');
    }
  }

  if (device_type !== undefined) {
    if (!isValidDeviceType(device_type)) {
      errors.push('device_type must be one of: temperature, humidity, motion, thermostat');
    }
  }

  if (location !== undefined) {
    if (!isNonEmptyString(location)) {
      errors.push('location must be a non-empty string');
    }
  }

  if (configuration !== undefined) {
    if (typeof configuration !== 'object') {
      errors.push('configuration must be an object');
    }
  }

  if (errors.length > 0) {
    return validationError(res, errors);
  }

  const cleanedData = {};
  if (device_name) cleanedData.device_name = device_name.trim();
  if (device_type) cleanedData.device_type = device_type;
  if (home_id !== undefined) cleanedData.home_id = home_id;
  if (location) cleanedData.location = location.trim();
  if (configuration !== undefined) cleanedData.configuration = configuration;

  req.body = cleanedData;
  next();
};

module.exports = {
  validateDevice,
  validateDeviceUpdate
};
