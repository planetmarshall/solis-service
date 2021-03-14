import json
from base64 import b64decode
import struct

import pandas as pd


def decode_elements(data, data_format, offset):
    required_size = struct.calcsize(data_format)
    for i in range(offset, len(data) - required_size + 1):
        yield i, struct.unpack_from(data_format, data, i)[0]


def decode_candidate(entry, data_format, offset):
    candidate = {"Time": entry["timestamp"]}
    candidate.update(decode_elements(b64decode(entry["data"]), data_format, offset))
    return candidate


def decode_candidates(file, data_format, length, offset):
    for row in file:
        entry = json.loads(row)
        if entry["length"] == length:
            yield decode_candidate(entry, data_format, offset)


def load_exported_data(data_file):
    return pd.read_excel(data_file, skiprows=3)


def load_candidates(log_file, data_format, offset=0):
    with open(log_file) as fp:
        candidates = pd.DataFrame.from_dict(decode_candidates(fp, data_format, 246, offset))
        candidates["Time"] = pd.to_datetime(candidates["Time"])
        return candidates


def column_correlations(expected, candidates, test_column):
    comparison = pd.merge_asof(expected[["Time", test_column]], candidates, on="Time")
    columns = [i for i in comparison.columns if i not in (test_column, "Time")]
    correlations = [(column, comparison[test_column].corr(comparison[column])) for column in columns]
    return pd.DataFrame(correlations, columns=["index", "correlation"])\
        .set_index("index")\
        .sort_values(by="correlation", ascending=False)


def best_matches(expected: pd.DataFrame, log, data_format):
    candidates = load_candidates(log, data_format)
    excluded_columns = [
        'Time',
        'InverterSN',
        'Data LoggerSN',
        'Alert Details',
        'Alert Code',
        'Inverter Status',
        'System Time'
    ]
    test_columns = [column for column in expected.columns if column not in excluded_columns]
    for test_column in test_columns:
        comparison = merge_comparison(expected, candidates, test_column)
        correlations = column_correlations(comparison, test_column)
        for correlation in correlations[:5].itertuples():
            yield {
                "column": test_column,
                "correlation": correlation.correlation,
                "field": correlation.Index,
                "format": data_format
            }


