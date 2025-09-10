const axios = require('axios');
const Device = require('./models/Device');
const TIMEOUT = 10000;

class DeviceManager {
  constructor() {
    this.monolithUrl = process.env.MONOLITH_URL || 'http://localhost:8080';
  }

  isTemperatureSensor(deviceType) {
    return deviceType === 'temperature';
  }

  async createDevice(deviceData) {
    if (this.isTemperatureSensor(deviceData.device_type)) {
      try {
        const sensorData = {
          name: deviceData.device_name,
          type: deviceData.device_type,
          location: deviceData.location || 'Unknown',
          unit: deviceData.configuration?.unit || '°C'
        };

        const response = await axios.post(`${this.monolithUrl}/api/v1/sensors`, sensorData, {
          timeout: TIMEOUT,
          headers: {
            'Content-Type': 'application/json'
          }
        });

        const sensor = response.data;
        return Device.fromJSON({
          device_id: sensor.id.toString(),
          device_name: sensor.name,
          device_type: sensor.type,
          home_id: deviceData.home_id, // сейчас не используется
          location: sensor.location,
          configuration: {
            unit: sensor.unit,
            value: sensor.value,
            status: sensor.status
          },
          created_at: sensor.created_at || new Date().toISOString()
        });
      } catch (error) {
        if (error.response) {
          throw new Error(`Monolith error: ${error.response.data.message || error.response.statusText}`);
        }
        throw new Error(`Failed to create temperature device: ${error.message}`);
      }
    } else {
      throw new Error(`Device type '${deviceData.device_type}' is not supported yet`);
    }
  }

  async getDeviceById(deviceId) {
    try {
      const response = await axios.get(`${this.monolithUrl}/api/v1/sensors/${deviceId}`, {
        timeout: TIMEOUT
      });

      const sensor = response.data;
      return Device.fromJSON({
        device_id: sensor.id.toString(),
        device_name: sensor.name,
        device_type: sensor.type,
        home_id: null, // Пока не используется
        location: sensor.location,
        configuration: {
          unit: sensor.unit,
          value: sensor.value,
          status: sensor.status
        },
        created_at: sensor.created_at || new Date().toISOString()
      });
    } catch (error) {
      if (error.response && error.response.status === 404) {
        return null;
      }
      if (error.response) {
        throw new Error(`Monolith error: ${error.response.data.message || error.response.statusText}`);
      }
      throw new Error(`Failed to get device: ${error.message}`);
    }
  }

  async getAllDevices() {
    try {
      const response = await axios.get(`${this.monolithUrl}/api/v1/sensors`, {
        timeout: TIMEOUT
      });

      return response.data
        .filter(sensor => sensor.type === 'temperature')
        .map(sensor => Device.fromJSON({
          device_id: sensor.id.toString(),
          device_name: sensor.name,
          device_type: sensor.type,
          home_id: null, // Пока не используется
          location: sensor.location,
          configuration: {
            unit: sensor.unit,
            value: sensor.value,
            status: sensor.status
          },
          created_at: sensor.created_at || new Date().toISOString()
        }));
    } catch (error) {
      if (error.response) {
        throw new Error(`Monolith error: ${error.response.data.message || error.response.statusText}`);
      }
      throw new Error(`Failed to get devices: ${error.message}`);
    }
  }

  // Для обновления данных нужно сделать 2 запроса в Монолит
  async updateDevice(deviceId, updateData) {
    try {
      let updatedSensor = null;

      const sensorMetadataUpdate = {};
      const sensorValueUpdate = {};

      if (updateData.device_name) sensorMetadataUpdate.name = updateData.device_name;
      if (updateData.device_type) sensorMetadataUpdate.type = updateData.device_type;
      if (updateData.location) sensorMetadataUpdate.location = updateData.location;
      if (updateData.configuration?.unit) sensorMetadataUpdate.unit = updateData.configuration.unit;

      if (updateData.configuration?.value !== undefined) sensorValueUpdate.value = updateData.configuration.value;
      if (updateData.configuration?.status) sensorValueUpdate.status = updateData.configuration.status;

      console.log(`🔧 Updating device ${deviceId}`);
      console.log(`📝 Metadata update:`, JSON.stringify(sensorMetadataUpdate, null, 2));
      console.log(`📊 Value update:`, JSON.stringify(sensorValueUpdate, null, 2));

      if (Object.keys(sensorMetadataUpdate).length > 0) {
        console.log(`🔄 Making PUT request to update sensor metadata`);
        const metadataResponse = await axios.put(`${this.monolithUrl}/api/v1/sensors/${deviceId}`, sensorMetadataUpdate, {
          timeout: TIMEOUT,
          headers: {
            'Content-Type': 'application/json'
          }
        });
        updatedSensor = metadataResponse.data;
        console.log(`✅ Sensor metadata updated successfully`);
      }

      if (Object.keys(sensorValueUpdate).length > 0) {
        console.log(`🔄 Making PATCH request to update sensor value`);
        const valueResponse = await axios.patch(`${this.monolithUrl}/api/v1/sensors/${deviceId}/value`, sensorValueUpdate, {
          timeout: TIMEOUT,
          headers: {
            'Content-Type': 'application/json'
          }
        });
        console.log(`✅ Sensor value updated successfully`);

        if (valueResponse.data && valueResponse.data.id) {
          updatedSensor = valueResponse.data;
        } else {
          console.log(`ℹ️ PATCH response incomplete, fetching current sensor data`);
          const currentResponse = await axios.get(`${this.monolithUrl}/api/v1/sensors/${deviceId}`, {
            timeout: TIMEOUT
          });
          updatedSensor = currentResponse.data;
        }
      }

      if (!updatedSensor) {
        console.log(`ℹ️ No updates to apply, fetching current sensor data`);
        const currentResponse = await axios.get(`${this.monolithUrl}/api/v1/sensors/${deviceId}`, {
          timeout: TIMEOUT
        });
        updatedSensor = currentResponse.data;
      }

      return Device.fromJSON({
        device_id: updatedSensor.id.toString(),
        device_name: updatedSensor.name,
        device_type: updatedSensor.type,
        home_id: null, // Пока не используется
        location: updatedSensor.location,
        configuration: {
          unit: updatedSensor.unit,
          value: updatedSensor.value,
          status: updatedSensor.status
        },
        created_at: updatedSensor.created_at || new Date().toISOString()
      });
    } catch (error) {
      if (error.response && error.response.status === 404) {
        throw new Error('Device not found');
      }
      if (error.response) {
        throw new Error(`Monolith error: ${error.response.data.message || error.response.statusText}`);
      }
      throw new Error(`Failed to update device: ${error.message}`);
    }
  }

  // Delete device
  async deleteDevice(deviceId) {
    try {
      await axios.delete(`${this.monolithUrl}/api/v1/sensors/${deviceId}`, {
        timeout: TIMEOUT
      });

      return true;
    } catch (error) {
      if (error.response && error.response.status === 404) {
        throw new Error('Device not found');
      }
      if (error.response) {
        throw new Error(`Monolith error: ${error.response.data.message || error.response.statusText}`);
      }
      throw new Error(`Failed to delete device: ${error.message}`);
    }
  }

}

module.exports = new DeviceManager();
