class Device {
  constructor(data) {
    this.device_id = data.device_id;
    this.device_name = data.device_name;
    this.device_type = data.device_type;
    this.home_id = data.home_id;
    this.location = data.location;
    this.configuration = data.configuration || {};
    this.created_at = data.created_at || new Date().toISOString();
  }

  toJSON() {
    return {
      device_id: this.device_id,
      device_name: this.device_name,
      device_type: this.device_type,
      home_id: this.home_id, //сейчас не используется
      location: this.location,
      configuration: this.configuration,
      created_at: this.created_at
    };
  }

  static fromJSON(json) {
    return new Device(json);
  }
}

module.exports = Device;
