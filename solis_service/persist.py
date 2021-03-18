from contextlib import contextmanager

from .persistence.influxdb_persistence_client import InfluxDbPersistenceClient


@contextmanager
def persistence_client(config):
    try:
        persistence_type = config["persistence"]
        if persistence_type == "influxdb":
            client = InfluxDbPersistenceClient(**config["influxdb"])
        else:
            raise ValueError(f"persistence type: {persistence_type}")
    finally:
        client.close()
