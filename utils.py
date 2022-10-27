import json


def json_loads(row: str):
    try:
        return json.loads(row.replace("\"", "\\\"").replace("\'", "\"")) if row != "NA" and row is not None else {}
    except json.decoder.JSONDecodeError:
        return {}
