import asyncio
from datetime import datetime
from io import BytesIO
import struct
import argparse
import logging

from .parse import parse_inverter_message


__clock = 0
logger = logging.getLogger("solis_service")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def increment_clock():
    global __clock
    return ++__clock & 255


def _checksum(buffer):
    lrc = 0
    for b in buffer[1:]:
        lrc = (lrc + b) & 255
    return struct.pack("<B", lrc & 255)


def _server_response(mode):
    buffer = BytesIO()
    header = b'\xa5\n\x00\x10'
    buffer.write(header)
    buffer.write(mode)
    buffer.write(struct.pack("<B", increment_clock()))
    prefix = b'\x01\xc2\xe8\xd7\xf0\x02\x01'
    buffer.write(prefix)
    timestamp = int(datetime.utcnow().timestamp())
    buffer.write(struct.pack("<I", timestamp))
    suffix = b'\x00\x00\x00\x00'
    buffer.write(suffix)
    buffer.write(_checksum(buffer.getvalue()))
    buffer.write(b'\x15')

    return buffer.getvalue()


def _heartbeat_response():
    return _server_response(b'\x11')


def _data_response():
    return _server_response(b'\x12')


def _is_heartbeat(message):
    return len(message) == 99


def _is_data_packet(message):
    return len(message) == 246


async def handle_inverter_message(reader, writer):
    buffer_size = 512
    message = await reader.read(buffer_size)

    if _is_heartbeat(message):
        logger.debug(f'Received heartbeat message from {writer.transport.get_extra_info("peername")}')
        writer.write(_heartbeat_response())

    elif _is_data_packet(message):
        writer.write(_data_response())
        inverter_data = parse_inverter_message(message)
        logger.debug(f'Received data message from {writer.transport.get_extra_info("peername")}')
        logger.debug(f'data message: {inverter_data}')

    writer.close()


async def main(hostname, port):
    logger.info(f"Starting server on {hostname}:{port}")
    server = await asyncio.start_server(handle_inverter_message, hostname, port)

    async with server:
        await server.serve_forever()


def run():
    parser = argparse.ArgumentParser(
        description="Receive messages from a Solis/Ginsong inverter and persist to a database")
    parser.add_argument("--hostname", help="IP address for the server host", default="localhost")
    parser.add_argument("--port", help="Port for the server host", default=9042)
    parser.add_argument("--debug", help="turn on debug logging", default=False, action="store_true")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    asyncio.run(main(args.hostname, args.port))


if __name__ == "__main__":
    run()
