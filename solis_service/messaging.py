from datetime import datetime
from io import BytesIO
from functools import reduce
from struct import unpack_from, pack

import pint


ureg = pint.UnitRegistry()


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


def mock_server_response(clock, mode, timestamp=None):
    unix_time = int(datetime.utcnow().timestamp() if timestamp is None else timestamp)
    buffer = BytesIO()
    header = b'\xa5\n\x00\x10'
    buffer.write(header)
    buffer.write(mode)
    buffer.write(pack("<B", clock))
    prefix = b'\x01\xc2\xe8\xd7\xf0\x02\x01'
    buffer.write(prefix)
    buffer.write(pack("<I", unix_time))
    suffix = b'\x00\x00\x00\x00'
    buffer.write(suffix)
    checksum_data = buffer.getvalue()
    buffer.write(pack("<B", checksum_byte(checksum_data[1:])))
    buffer.write(b'\x15')

    return buffer.getvalue()
