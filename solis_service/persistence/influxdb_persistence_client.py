import asyncio
from datetime import datetime
from concurrent.futures.thread import ThreadPoolExecutor


from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


def to_influx_measurement(timestamp, data):
    return {
        "measurement": f"solis_inverter_{data['inverter_serial_number']}",
        "time": timestamp,
        "fields": {key: value.magnitude for key, value in data.items() if key != "inverter_serial_number"}
    }


class InfluxDbPersistenceClient:
    description = "InfluxDb Persistence Client"

    def __init__(self, url, token, org, bucket):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.bucket = bucket
        self.writer = self.client.write_api(write_options=SYNCHRONOUS)

    async def write_measurement(self, measurement):
        timestamp = datetime.utcnow().isoformat()
        record = to_influx_measurement(timestamp, measurement)
        with ThreadPoolExecutor() as pool:
            return asyncio.get_running_loop().run_in_executor(pool, self.writer.write, self.bucket, record=record)

    def close(self):
        self.writer.close()
        self.client.close()