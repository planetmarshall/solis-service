from struct import unpack_from

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
        "total_active_generation":          float(unpack_from("<I", message, 120)[0]) * ureg.kilowatt_hour, # or 130
        "generation_yesterday":             0.1 * unpack_from("<H", message, 128)[0] * ureg.kilowatt_hour,
        "power_grid_total_apparent_power":  float(unpack_from("<I", message, 142)[0]) * ureg.volt_ampere,
    }
