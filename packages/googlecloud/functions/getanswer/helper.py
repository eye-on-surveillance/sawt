"""Parse field from JSON or raise error if missing"""
def parse_field(request_json, field: str):
    if request_json and field in request_json:
        return request_json[field]
    else:
        raise ValueError(f"JSON is invalid, or missing a '${field}' property")