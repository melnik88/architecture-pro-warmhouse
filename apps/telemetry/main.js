const axios = require('axios');
const TIMEOUT = 10000;

class TelemetryService {
  constructor() {
    this.deviceManagerUrl = process.env.DEVICE_MANAGER_URL || 'http://localhost:8082';
    this.temperatureApiUrl = process.env.TEMPERATURE_API_URL || 'http://localhost:8081';
    this.intervalId = null;
    this.isRunning = false;
  }

  /**
   * Запуск процесса сбора телеметрии выполняется каждые 10 секунд
   */
  start() {
    if (this.isRunning) {
      console.log('⚠️ Telemetry service is already running');
      return;
    }

    console.log('🚀 Starting telemetry service...');
    this.isRunning = true;

    this.collectTelemetryData();

    this.intervalId = setInterval(() => {
      this.collectTelemetryData();
    }, TIMEOUT);

    console.log('✅ Telemetry service started - collecting data every 10 seconds');
  }

  stop() {
    if (!this.isRunning) {
      console.log('⚠️ Telemetry service is not running');
      return;
    }

    console.log('🛑 Stopping telemetry service...');

    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    this.isRunning = false;
    console.log('✅ Telemetry service stopped');
  }

  async collectTelemetryData() {
    try {
      console.log('📊 Starting telemetry data collection...');

      const devices = await this.getAllDevices();
      console.log(`📱 Found ${devices.length} devices`);

      if (devices.length === 0) {
        console.log('ℹ️ No devices found, skipping telemetry collection');
        return;
      }

      for (const device of devices) {
        await this.processDevice(device);
      }

      console.log('✅ Telemetry data collection completed');
    } catch (error) {
      console.error('❌ Error during telemetry collection:', error.message);
    }
  }

  async getAllDevices() {
    try {
      const response = await axios.get(`${this.deviceManagerUrl}/api/v1/devices`, {
        timeout: TIMEOUT,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data && response.data.success && response.data.data) {
        return response.data.data;
      }

      return [];
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        throw new Error('Unable to connect to device-manager service');
      }
      throw new Error(`Error fetching devices: ${error.message}`);
    }
  }

  async processDevice(device) {
    try {
      console.log(`🔍 Processing device: ${device.device_name} (${device.device_type})`);

      // Проверить, является ли устройство температурным датчиком
      if (device.device_type === 'temperature') {
        await this.processTemperatureSensor(device);
      } else {
        console.log(`⚠️ Device type '${device.device_type}' is not supported`);
      }
    } catch (error) {
      console.error(`❌ Error processing device ${device.device_name}:`, error.message);
    }
  }

  /**
   * Обработка температурного датчика
   */
  async processTemperatureSensor(device) {
    try {
      console.log(`🌡️ Processing temperature sensor: ${device.device_name} at ${device.location}`);

      const temperatureResponse = await axios.get(`${this.temperatureApiUrl}/temperature`, {
        params: { location: device.location },
        timeout: TIMEOUT,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const temperatureData = temperatureResponse.data;
      console.log(`📊 Got temperature data: ${temperatureData.temperature}°C for ${device.location}`);

      const updateData = {
        configuration: {
          ...device.configuration,
          value: temperatureData.temperature,
          status: temperatureData.status,
          unit: temperatureData.unit,
          last_reading: temperatureData.timestamp,
          sensor_id: temperatureData.sensor_id
        }
      };

      const updateResponse = await axios.put(
        `${this.deviceManagerUrl}/api/v1/devices/${device.device_id}`,
        updateData,
        {
          timeout: TIMEOUT,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (!updateResponse.data || !updateResponse.data.success) {
        throw new Error('Failed to update device - invalid response');
      }

      console.log(`✅ Successfully updated temperature for ${device.device_name}`);
      return updateResponse.data.data;
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        throw new Error('Unable to connect to device-manager service');
      }

      if (error.response && error.response.status === 404) {
        throw new Error('Device not found');
      }

      throw new Error(`Error processing temperature sensor ${device.device_name}: ${error.message}`);
    }
  }

}

module.exports = TelemetryService;
