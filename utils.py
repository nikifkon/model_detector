import json


def json_loads(row):
    try:
        return json.loads(row.decode('utf-8').replace("\"", "\\\"").replace("\'", "\"")) if row != "NA" and row is not None else {}
    except json.decoder.JSONDecodeError:
        return {}
