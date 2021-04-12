import json

from flask import Flask, request

from input_validator import validate_request
from solver import cvrp
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

app = Flask(__name__)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/api/solveVehicleRoutingProblem', methods=['POST'])
def solve_vehicle_routing_problem():
    input_json = request.get_json()
    validate_request(input_json)
    response = cvrp.solve_vehicle_routing_problem(input_json)
    return json.dumps(response)
