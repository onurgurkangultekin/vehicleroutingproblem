import copy
import json

from solver.or_tools import solve


def create_duration_matrix(matrix):
    duration_matrix = copy.deepcopy(matrix)
    n = len(duration_matrix)
    for row in duration_matrix:
        row.append(0)
    duration_matrix.append([0 for _ in range(n + 1)])
    return duration_matrix


def create_vehicle_data(vehicles, duration_matrix):
    vehicle_data = {'starts': [v['start_index'] for v in vehicles.values()],
                    'num_vehicles': len(vehicles),
                    'ends': [len(duration_matrix) - 1 for _ in range(len(vehicles))],
                    'vehicle_capacities': [v['capacity'][0] for v in vehicles.values()]}
    return vehicle_data


def get_demands(vehicles, jobs, n):
    demands = [0 for _ in range(n)]
    for vehicle in vehicles.values():
        demands[vehicle['start_index']] = 0
    for job in jobs.values():
        demands[job['location_index']] = job['delivery'][0]
    return demands


def solve_vehicle_routing_problem(input_json):
    vehicles = {v['id']: v for v in input_json['vehicles']}
    jobs = {j['id']: j for j in input_json['jobs']}
    matrix = input_json['matrix']
    duration_matrix = create_duration_matrix(matrix)
    vehicle_data = create_vehicle_data(vehicles, duration_matrix)
    demands = get_demands(vehicles, jobs, len(duration_matrix))
    data = {'duration_matrix': duration_matrix,
            'num_vehicles': vehicle_data['num_vehicles'],
            'starts': vehicle_data['starts'],
            'ends': vehicle_data['ends'],
            'demands': demands,
            'vehicle_capacities': vehicle_data['vehicle_capacities'],
            'vehicle_ids': {v['start_index']: v['id'] for v in vehicles.values()},
            'job_ids': {j['location_index']: j['id'] for j in jobs.values()}}
    response = solve(data)
    return response


if __name__ == '__main__':
    with open('../data/input.json') as f:
        input_json = json.loads(f.read())
    solve_vehicle_routing_problem(input_json)
