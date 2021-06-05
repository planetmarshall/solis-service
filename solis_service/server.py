import argparse
import asyncio
from configparser import ConfigParser
import functools
import logging
import logging.config
import os
import traceback

from .messaging import (
    parse_header,
    parse_inverter_message,
    mock_server_response,
    checksum_byte
)
from .persistence import persistence_client


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


def _is_heartbeat(header):
    return header['type'] == 0x41

def _is_data_packet(header):
    return header['type'] == 0x42


async def handle_inverter_message(persist, reader, writer):
    try:
        while True:
            msghdr = await reader.readexactly(11)
            header = parse_header(msghdr)
            payload_plus_footer = await reader.readexactly(header['payload_length']+2)
            message = msghdr + payload_plus_footer

            if message[0] == 0xa5 and message[-1] == 0x15 and message[-2] == checksum_byte(message[1:-2]):
                if _is_heartbeat(header):
                    logger.debug(f'Received heartbeat message from {writer.transport.get_extra_info("peername")} serial={header["serialno"]}')

                elif _is_data_packet(header):
                    inverter_data = parse_inverter_message(message)
                    logger.debug(f'Received data message from {writer.transport.get_extra_info("peername")}')
                    logger.debug(f'data message: {inverter_data}')
                    logger.debug(f'persisting data with {persist.description}')
                    result = await persist.write_measurement(inverter_data)
                    logger.debug(f'persistence result: {result}')

                else:
                    logger.debug(f'Unknown packet from {writer.transport.get_extra_info("peername")}: {message} {header}')

                writer.write(mock_server_response(header, payload_plus_footer))

            else:
                    logger.debug(f'Malformed packet from {writer.transport.get_extra_info("peername")}: {message[0]} {message[-1]}')
                    break

    except Exception:
        traceback.print_exc()

    finally:
        writer.close()
        await writer.wait_closed()


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
