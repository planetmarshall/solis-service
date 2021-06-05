from datetime import datetime
from io import BytesIO
from functools import reduce
from struct import unpack_from, pack

import pint


ureg = pint.UnitRegistry()

def parse_header(msghdr):
    [ payload_length, type, resp_idx, req_idx, serialno ] = unpack_from("<xHxBBBI", msghdr, 0)
    return {
        "payload_length": payload_length,
        "type": type,
        "resp_idx": resp_idx,
        "req_idx": req_idx,
        "serialno": serialno
    }

def parse_inverter_message(message):
    return {
        "inverter_serial_number":           message[32:48].decode("ascii").rstrip(),
        "inverter_temperature":             0.1 * unpack_from("<H", message, 48)[0] * ureg.centigrade,
        "dc_voltage_pv1":                   0.1 * unpack_from("<H", message, 50)[0] * ureg.volt,  # could also be 52
        "dc_current":                       0.1 * unpack_from("<H", message, 54)[0] * ureg.amperes,
        "ac_current_t_w_c":                 0.1 * unpack_from("<H", message, 62)[0] * ureg.amperes,
        "ac_voltage_t_w_c":                 0.1 * unpack_from("<H", message, 68)[0] * ureg.volt,
        "ac_output_frequency":              0.01 * unpack_from("<H", message, 70)[0] * ureg.hertz,
        "daily_active_generation":          0.01 * unpack_from("<H", message, 76)[0] * ureg.kilowatt_hour,
        "total_dc_input_power":             float(unpack_from("<I", message, 116)[0]) * ureg.watts,
        "total_active_generation":          float(unpack_from("<I", message, 120)[0]) * ureg.kilowatt_hour,  # or 130
        "generation_yesterday":             0.1 * unpack_from("<H", message, 128)[0] * ureg.kilowatt_hour,
        "power_grid_total_apparent_power":  float(unpack_from("<I", message, 142)[0]) * ureg.volt_ampere,
    }


def checksum_byte(buffer):
    return reduce(lambda lrc, x: (lrc + x) & 255, buffer) & 255


def mock_server_response(header, request_payload, timestamp=None):
    unix_time = int(datetime.utcnow().timestamp() if timestamp is None else timestamp)
    
    # don't know what's the meaning of these magic values
    # the first byte seems to usually echo the first byte of the request payload
    payload = pack("<BBIBBBB", request_payload[0], 0x01, unix_time, 0xaa, 0xaa, 0x00, 0x00)

    resp_type = header['type'] - 0x30
    header = pack("<BHBBBBI", 0xa5, len(payload), 0x00, resp_type, header['req_idx'], header['req_idx'], header['serialno'])
    message = header + payload
    message += pack("BB", checksum_byte(message[1:]), 0x15)
    return message
