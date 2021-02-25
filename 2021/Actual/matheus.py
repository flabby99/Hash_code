# TODO import your packages


def matheus_solution(input_info, **kwargs):
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
        line_to_append = [i, 1]
        starting_streets = find_streets_at_intersection(i, street_info)
        num_streets = len(starting_streets)
        if len(starting_streets) != 0:
            for j in range(num_streets):
                if j <= D:
                    street_name = starting_streets[j][2]
                    line_to_append.append((street_name, 1))
                # Also want to try D / num_streets
            solution.append(line_to_append)

    return solution, 0