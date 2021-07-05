import json
from flask import Response

ERROR_CODES = {
    "bad_request": 400,
    "server_error": 500
}


def client_error_response(description, error_code):
    return _error_response(description, error_code)


def server_error_response(error_code):
    return _error_response(error_code=error_code)


def _error_response(description="Internal server error", error_code=500):
    if error_code is None:
        error_code = 500

    payload = json.dumps({
        "service_name": "standings",
        "error_code": error_code,
        "description": description
    })

    return Response(payload, status=error_code, mimetype='application/json')
