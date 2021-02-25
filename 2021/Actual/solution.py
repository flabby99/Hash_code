"""
Skeleton code for our solution, to be updated on the day.

The main things we will need to do are:
1. write an input reader in read_file
2. write an output writer in write_file
3. change filenames in main
4. write solutions in matheus, ham, or sean

Generally speaking, I have marked things may need to be changed with TODO.
You should be able to view these nicely in vs code TODOS bar.
"""

import os
from datetime import datetime
from time import time
from copy import copy
import traceback
from pprint import pprint

import numpy as np

from utils import line_to_data
from utils import zip_dir
from utils import add_params
from hyper_params import return_hyperparam_list

# import your solution here
try:
    from matheus import matheus_solution
except Exception as e:
    print(e, "occurred in matheus file, printing trace:")
    traceback.print_exc()
try:
    from ronaldo import ronaldo_solution
except Exception as e:
    print(e, "occurred in ham file, printing trace:")
    traceback.print_exc()
try:
    from sean import sean_solution
except Exception as e:
    print(e, "occurred in sean file, printing trace:")
    traceback.print_exc()


def read_file(input_location):
    """
    Return info from the input_location.

    Parameters
    ---------
    input_location : str
        Full path to input location.

    Returns
    -------
    input_info : object
        The information from the problem.

    """
    with open(input_location, "r") as f:
        # Line 1 - D I S V F, all int
        # D - duration, I - num intersections, S - num streets
        # V - num cars, F - bonus score for cars reaching destination
        D, I, S, V, F = line_to_data(f.readline(), np_array=False, dtype=int)
        
        # Next S lines contain descriptions of the streets
        street_info = []
        for _ in range(S):
        # line: B E NAME L
        # B, E - intersections at start and end of street
        # Name - string consisting of between 3 and 30
        # L - the time it takes a car to traverse the street
            B, E, S_Name, L = line_to_data(f.readline(), np_array=False, dtype=str)
            B = int(B)
            E = int(E)
            L = int(L)
            street_info.append([B, E, S_Name, L])

        # Next V lines describe the paths of each car
        # line: P P_names
        # P - the number of streets the car needs to travel
        # Space separated names of the streets in order (P of these)
        car_info = []
        for _ in range(V):
            line_info = line_to_data(f.readline(), np_array=False, dtype=str)
            P = int(line_info[0])
            line_info = [P,] + line_info[1:]
            car_info.append(line_info)
    
        input_info = (D, I, S, V, F, street_info, car_info)

    return input_info


def write_file(output_location, solution):
    """
    Write to output_location containing the solution.

    Parameters
    ----------
    output_location : str
        Full path to output location.
    solution : ??
        Could be anything, but usually is a numpy array.

    Returns
    -------
    None

    """
    with open(output_location, "w") as f:
        # The first line integer A, the number of intersections scheduled

        # Pass a list of intersection schedules

        # For each of these A
        # First line i - the ID of the intersection
        # Second line E_i - the number of incoming streets in the schedule
        # E_i lines (order and duration of green lights)
        # StreetName T (how long this street will have a green light)

        f.write("{}\n".format(len(solution)))
        for val in solution:
            ID_i, E_i = val[0], val[1]
            f.write(f"{ID_i}\n{E_i}\n")
            lights_info = val[2:]
            for light in lights_info:
                street_name, light_time = light
                f.write(f"{street_name} {light_time}\n")    


def print_solution(solution):
    """
    Print things relevant to the solution.

    For example, you could print the number of taxis with no rides.
    Or the max number of rides assigned to a taxi.
    """
    # TODO print actually useful things, like summary information.
    # print("\tSolution is: {}".format(solution))
    print("\tCan print solution information")
    return


def run(input_location, output_location, method, **kwargs):
    """
    Read the file, calculate solution, and write the results.

    Parameters
    ----------
    input_location : str
        The full path to the location of the input file.
    output_location : str
        The full path to the location of the output file.
    method : function
        Which function to run info on as method(info, **kwargs)
    **kwargs :
        keyword arguments to pass into method

    Returns
    -------
    float : score
        The score for this run (return 0 if you can't calculate the score).

    """
    start_time = time()
    input_info = read_file(input_location)
    solution, score = method(input_info, **kwargs)
    write_file(output_location, solution)
    print("\tCompleted in {:.2f} seconds".format(time() - start_time))
    print_solution(solution)
    print("Scored:", score)
    return score


def main(method, filenames, parameter_list, skip, seed):
    """
    Parse the input information and run the main loop.

    What this does in full is:
    1.  Create a new directory in the directory "outputs" with current time.
    2.  Zip the source code into that directory.
    3.  Loop over the filenames, running the function run on each one that
        is not skipped. Also writes the score achieved into Result.txt
        in the directory created in step 1.
    4.  Adds up all the scores and prints the total score for this run.

    Parameters
    ----------
    method : function
        The function to do the computation, method(info, **kwargs).
    filenames : list of str
        The names of the files in input_files dir to run on
    parameter_list : list of dict
        The set of kwargs to pass to method for each filename
        len(parameter_list) must equal len(filenames)
    skip : list of bool
        skip[i] == True indicates you should skip execution of filename[i]
    seed : int
        Seed for the random number generator

    Returns
    -------
    None

    Raises
    ------
    ValueError:
        if filenames, parameter_list, and skip are not equal length.

    """
    # Initial checking to see if the length of the params is correct
    individual_list_size = (len(filenames) + len(parameter_list) + len(skip)) / 3
    if individual_list_size != len(filenames):
        raise ValueError(
            "Pass equal len filenames {} parameters {} and skips {}".format(
                len(filenames), len(parameter_list), len(skip)
            )
        )

    # Do setup of arrays etc.
    here = os.path.dirname(os.path.realpath(__file__))
    np.random.seed(seed)  # to reproduce results
    in_dir = "input_files"
    locations = [os.path.join(here, in_dir, filename) for filename in filenames]
    scores = np.zeros(len(locations))

    # Create a new directory at this time to compare to old solutions
    now = datetime.now()
    current_time = now.strftime("%H-%M-%S")
    out_dir = current_time
    out_dir = os.path.join(here, "outputs", out_dir)
    os.makedirs(out_dir, exist_ok=True)

    # Zip up the directory
    zip_loc = os.path.join(out_dir, "Source.zip")
    zip_dir(here, zip_loc, ".py")

    # Start the execution loop
    with open(os.path.join(out_dir, "Result.txt"), "w") as f:
        for i, (input_location, params) in enumerate(zip(locations, parameter_list)):

            # Ignore some files optionally
            if skip[i]:
                print("Skipping {}".format(input_location))
                continue

            # Setup and print what is happening
            print(
                "Working on {} with parameters {} using {}:".format(
                    os.path.basename(input_location), params, method.__name__
                )
            )
            output_location = os.path.join(
                out_dir, os.path.basename(input_location[:-3]) + ".out"
            )

            # TODO Put anything which may be useful to all solutions here
            params_copy = copy(params)
            params_copy["output_dir"] = out_dir
            params_copy["input_name"] = os.path.basename(input_location)

            # Actual running happens here
            score = run(input_location, output_location, method, **params_copy)

            # Write the achieved score to disk
            scores[i] = score
            f.write("{} {}\n".format(os.path.basename(input_location)[:-3], score))

        # Prints the final score
        last_str = "Total score: {}".format(np.sum(scores))
        f.write(last_str)
        print(last_str)


def setup_params(filenames):
    """
    Here you can set up specific parameters for each file in filenames.

    The output format should be a list of dictionaries. 
    You can either manually make this list of dictionaries
    or use the helper function add_params which can be seen in use
    in the default version of this function.

    """
    # At the very least you must return this from the function,
    # A list of blank dictionaries.
    param_list = [{}, {}, {}, {}, {}, {}]

    # This holds which iteration of the main loop you are on
    # Can be useful to know in some circumstances.
    param_list = add_params(
        param_list, "iter", [str(i + 1) for i in range(len(filenames))]
    )

    # TODO decide here if you are doing any searching
    # Leave this as True if you are not doing hyper-param searching
    # Ignore all the below things if not using hyper-param searching
    use_hyper_params = True
    param_list = add_params(param_list, "search", not use_hyper_params)
    if use_hyper_params:
        hyper_params = return_hyperparam_list()
        param_list = add_params(param_list, "objective_args", hyper_params)

    return param_list


if __name__ == "__main__":
    """This is where most things you should change are."""
    # TODO Change the method here to the desired one
    main_method = sean_solution

    # TODO change this to be the actual filenames
    main_filenames = ["a.txt", "b.txt", "c.txt", "d.txt", "e.txt", "f.txt"]

    # TODO Indicate which files to run
    main_skip = [False, False, False, False, False, False]

    # TODO Set the random seed for reproducibility
    main_seed = 1

    # TODO inside of setup_params you can change parameters for specific files.
    main_param_list = setup_params(main_filenames)

    main(main_method, main_filenames, main_param_list, main_skip, main_seed)


    # TODO Set the random seed for reproducibility
    main_seed = 1

    # TODO inside of setup_params you can change parameters for specific files.
    main_param_list = setup_params(main_filenames)

    main(main_method, main_filenames, main_param_list, main_skip, main_seed)
