
Vehicle Routing Problem Solver
===================================

For given list of vehicles, list of jobs and cost matrix, Vehicle Routing Problem Solver
App will find the best route list for each vehicle in the list with respect to time cost.

Google OR Tools are used to solve the optimization problem.
Cost matrix, demands and capacities are taken into account.
Service time information is not used.

Webservice endpoint
"""""""""""""""""""
* Url: http://localhost:5000/api/solveVehicleRoutingProblem
* [GET], application/json

Input definition (JSON):
""""""""""""""""
* Vehicle: id, start_index, capacity
* Job: id, location_index, delivery list, service
* Matrix: list of list of integer values (time cost matrix)


Output Definition :
"""""""""""""""""""""
* total_delivery_duration,
* routes
    * vehicle_id
    * delivery_duration
    * jobs