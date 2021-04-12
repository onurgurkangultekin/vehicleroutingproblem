from jsonschema import validate, ValidationError
from werkzeug.exceptions import BadRequest

SCHEMA_CVRP = {
    'properties': {
        'vehicles': {'type': 'array'},
        'jobs': {'type': 'array'},
        'matrix': {'type': 'array'},
    },
    "additionalProperties": False,
    'required': ['vehicles', 'jobs', 'matrix']
}


def validate_request(request):
    if not request:
        raise BadRequest('Invalid Request, no content in request body')
    try:
        validate(instance=request, schema=SCHEMA_CVRP)
    except ValidationError as validation_error:
        raise BadRequest(f"Invalid Request: {validation_error.message}")
