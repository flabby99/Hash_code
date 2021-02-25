"""Please place things here which may be useful to everyone."""

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
            if street[0] == intersection_idx:
                starting_streets.append(street)
        return starting_streets

    # Loop through the intersections
    for i in range(I):
