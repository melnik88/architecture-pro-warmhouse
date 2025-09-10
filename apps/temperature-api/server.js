const express = require('express');

const app = express();
const PORT = process.env.PORT || 8081;

app.use(express.json());

function generateRandomTemperature(location = 'living room') {
  const locationRanges = {
    'living room': { min: 18, max: 25 },
    'bedroom': { min: 16, max: 23 },
    'kitchen': { min: 20, max: 28 },
    'bathroom': { min: 22, max: 26 },
    'outdoor': { min: -10, max: 35 },
    'garage': { min: 5, max: 30 }
  };

  const locationKey = location.toLowerCase();
  const range = locationRanges[locationKey];

  const temperature = Math.random() * (range.max - range.min) + range.min;
  return parseFloat(temperature.toFixed(1));
}

app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'temperature-api',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

app.get('/temperature', (req, res) => {
  const location = req.query.location || 'living room';
  const temperature = generateRandomTemperature(location);

  const response = {
    location: location,
    temperature: temperature,
    unit: '°C',
    timestamp: new Date().toISOString(),
    sensor_id: `temp_sensor_${location.replace(/\s+/g, '_').toLowerCase()}`,
    status: 'active'
  };

  console.log(`Temperature request for ${location}: ${temperature}°C`);
  res.json(response);
});

app.get('/temperature/:id', (req, res) => {
  const sensorId = req.params.id;

  // Генерируем случайную температуру для sensor ID
  const temperature = generateRandomTemperature();

  const response = {
    value: temperature,
    timestamp: new Date().toISOString(),
    status: 'active',
  };

  console.log(`Temperature request for sensor ID ${sensorId}: ${temperature}°C`);
  res.json(response);
});

app.use((err, req, res, next) => {
  console.error('Ошибка:', err.message);
  res.status(500).json({
    error: 'Внутренняя ошибка сервера',
    message: err.message,
    timestamp: new Date().toISOString()
  });
});

app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Не найдено',
    message: `Маршрут ${req.originalUrl} не найден`,
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🌡️  Temperature API server running on port ${PORT}`);
  console.log(`📍 Available endpoints:`);
  console.log(`   GET /health - Health check`);
  console.log(`   GET /temperature?location=<location> - Get temperature for location`);
  console.log(`   GET /temperature/:id - Get temperature for sensor ID`);
});

module.exports = app;
