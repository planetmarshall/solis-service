def to_influx_measurement(timestamp, data):
    return {
        "measurement": f"solis_inverter_{data['inverter_serial_number']}",
        "time": timestamp,
        "fields": {key: value.magnitude for key, value in data.items() if key != "inverter_serial_number"}
    }