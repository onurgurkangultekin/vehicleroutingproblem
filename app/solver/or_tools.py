"""Vehicles Routing Problem (VRP)."""
import sys

from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    sum_route_duration = 0
    for vehicle_loc_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_loc_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_loc_id)
        route_duration = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_duration += routing.GetArcCostForVehicle(previous_index, index, vehicle_loc_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'duration of the route: {} secs.\n'.format(route_duration)
        print(plan_output)
        sum_route_duration += route_duration
    print('Sum of the route durations: {} secs.'.format(sum_route_duration))


def prepare_solution(data, manager, routing, solution):
    """Prints solution on console."""
    result = {'total_delivery_duration': 0, 'routes': {}}
    sum_route_time = 0
    for vehicle_loc_id in range(data['num_vehicles']):
        vehicle_id = str(data['vehicle_ids'][vehicle_loc_id])
        result['routes'][vehicle_id] = {'jobs': []}
        index = routing.Start(vehicle_loc_id)
        route_duration = 0
        while not routing.IsEnd(index):
            route_index = manager.IndexToNode(index)
            if vehicle_loc_id != route_index:
                result['routes'][vehicle_id]['jobs'].append(str(data['job_ids'][route_index]))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_duration += routing.GetArcCostForVehicle(previous_index, index, vehicle_loc_id)
            result['routes'][vehicle_id]['delivery_duration'] = route_duration
        sum_route_time += route_duration
    result['total_delivery_duration'] = sum_route_time
    return result


def solve(data):
    """Solve the CVRP problem."""
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['duration_matrix']), data['num_vehicles'], data['starts'], data['ends'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def duration_callback(from_index, to_index):
        """Returns the duration between the two nodes."""
        # Convert from routing variable Index to duration matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['duration_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(duration_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    if 'time_windows' in data:
        # Add Time Windows constraint.
        time = 'Time'
        routing.AddDimension(
            transit_callback_index,
            sys.maxsize,  # allow waiting time
            sys.maxsize,  # maximum time per vehicle
            False,  # Don't force start cumul to zero.
            time)
        time_dimension = routing.GetDimensionOrDie(time)
        # Add time window constraints for each location except depot.
        for location_idx, time_window in enumerate(data['time_windows']):
            if location_idx in data['starts'] or location_idx in data['ends']:
                continue
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        # Add time window constraints for each vehicle start node.
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            for start_index in data['starts']:
                time_dimension.CumulVar(index).SetRange(
                    data['time_windows'][start_index][0],
                    data['time_windows'][start_index][1])
        for i in range(data['num_vehicles']):
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.Start(i)))
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.End(i)))

    # Add Capacity constraint.
    if 'demands' in data and 'vehicle_capacities' in data:
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['vehicle_capacities'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
        return prepare_solution(data, manager, routing, solution)
