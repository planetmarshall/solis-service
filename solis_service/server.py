import argparse
import asyncio
from configparser import ConfigParser
import functools
import logging
import logging.config
import os

from .messaging import (
    parse_inverter_message,
    mock_server_response
)
from .persistence import persistence_client


__clock = 0
logger = logging.getLogger("solis_service")


def load_config(config_file=None):
    if config_file is None:
        config_file_name = "solis-service.conf"
        candidates = [os.path.realpath(os.path.join(prefix, config_file_name))
                      for prefix in [".", "/etc", "/usr/local/etc"]]
        for candidate in candidates:
            if os.path.exists(candidate):
                config_file = candidate
        if config_file is None:
            raise ValueError("No config file found")

    config_file_path = os.path.realpath(config_file)
    logging.config.fileConfig(config_file)
    config = ConfigParser()
    config.read(config_file_path)
    return config


def increment_clock():
    global __clock
    return ++__clock & 255


def _heartbeat_response():
    return mock_server_response(increment_clock(), b'\x11')


def _data_response():
    return mock_server_response(increment_clock(), b'\x12')


def _is_heartbeat(message):
    return len(message) == 99


def _is_data_packet(message):
    return len(message) == 246


async def handle_inverter_message(persist, reader, writer):
    buffer_size = 512
    message = await reader.read(buffer_size)

    if _is_heartbeat(message):
        logger.debug(f'Received heartbeat message from {writer.transport.get_extra_info("peername")}')
        writer.write(_heartbeat_response())
        writer.close()

    elif _is_data_packet(message):
        writer.write(_data_response())
        writer.close()
        inverter_data = parse_inverter_message(message)
        logger.debug(f'Received data message from {writer.transport.get_extra_info("peername")}')
        logger.debug(f'data message: {inverter_data}')
        logger.debug(f'persisting data with {persist.description}')
        await persist.write_measurement(inverter_data)


async def main(hostname, port, config):
    logger.info(f"Starting server on {hostname}:{port}")
    with persistence_client(config) as client:
        server = await asyncio.start_server(functools.partial(handle_inverter_message, client), hostname, port)
        async with server:
            await server.serve_forever()


def run():
    parser = argparse.ArgumentParser(
        description="Receive messages from a Solis/Ginsong inverter and persist to a database")
    parser.add_argument("--config", help="load a config file")
    args = parser.parse_args()
    config = load_config(args.config)
    service_config = config["service"]
    hostname = service_config.get("hostname", "localhost")
    port = service_config.get("port", "9042")

    asyncio.run(main(hostname, int(port), config))


if __name__ == "__main__":
    run()
