import asyncio
import json
from base64 import b64encode
from datetime import datetime


async def _read_and_log_response(reader, writer):
    buffer_size = 1024
    data = await reader.read(buffer_size)
    print(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'target': writer.transport.get_extra_info("peername"),
        'data': b64encode(data).decode('ascii'),
        'length': len(data)})
    )

    return data


async def log_and_forward_response(reader, writer):
    data = await _read_and_log_response(reader, writer)
    writer.write(data)
    await writer.drain()


async def handle_inverter_message(inverter_reader, inverter_writer):
    server_reader, server_writer = await asyncio.open_connection('47.88.8.200', 10000)
    await log_and_forward_response(inverter_reader, server_writer)
    await log_and_forward_response(server_reader, inverter_writer)
    server_writer.close()
    inverter_writer.close()


async def main():
    server = await asyncio.start_server(handle_inverter_message,
            '192.168.10.9', 19042)

    print(f"serving on {server.sockets[0].getsockname()}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
