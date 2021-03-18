from contextlib import contextmanager

from .influxdb_persistence_client import InfluxDbPersistenceClient


@contextmanager
def persistence_client(config):
    client = None
    try:
        persistence_type = config["service"]["persistence"]
        if persistence_type == "influxdb":
            client = InfluxDbPersistenceClient(**config["influxdb"])
            yield client
        else:
            raise ValueError(f"persistence type: {persistence_type}")
    finally:
        if client is not None:
            client.close()
