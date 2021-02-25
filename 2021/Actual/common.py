"""Please place things here which may be useful to everyone."""

import numpy as np

def scorer(solution, D, F):
    """
    Award points for each car that finished its journey.
    
    Score is:
    For each car
    F + (D - T), where F is fixed bonus,
    and D - T is the time left in the simulation.

    """
    score = 0
    # for each car in the solution
    return score


def dumb_solution(input_info, **kwargs):
    D, I, S, V, F, street_info, car_info = input_info

    solution = []

    def find_streets_at_intersection(intersection_idx, street_info):
        starting_streets = []
        
        for street in street_info:
            if street[1] == intersection_idx:
                starting_streets.append(street)
        
        return starting_streets

    # Loop through the intersections

    for i in range(I):
        starting_streets = find_streets_at_intersection(i, street_info)
        num_streets = len(starting_streets)
        num_lights = min(num_streets, D)
        line_to_append = [i, num_lights]
        if len(starting_streets) != 0:
            for j in range(num_streets):
                if j <= D:
                    street_name = starting_streets[j][2]
                    line_to_append.append((street_name, 1))
                # Also want to try D / num_streets
            solution.append(line_to_append)

    return solution, 0


def random_solution(input_info, **kwargs):
    D, I, S, V, F, street_info, car_info = input_info

    solution = []

    def find_streets_at_intersection(intersection_idx, street_info):
        starting_streets = []
        
        for street in street_info:
            if street[1] == intersection_idx:
                starting_streets.append(street)
        
        return starting_streets

    # Loop through the intersections

    for i in range(I):
        starting_streets = find_streets_at_intersection(i, street_info)
        num_streets = len(starting_streets)
        num_lights = min(num_streets, D)
        random_times = np.random.randint(1, np.floor(D / num_lights), num_lights)
        line_to_append = [i, num_lights]
        # put the first light into line_to_append
        # iterate over the other lights
        for j in range(num_lights):
            street_name = starting_streets[j][2]
            line_to_append.append((street_name, random_times[j]))
            # Also want to try D / num_streets
        solution.append(line_to_append)

    return solution, 0
