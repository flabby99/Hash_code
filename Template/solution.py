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

import numpy as np

from utils import line_to_data
from utils import zip_dir
from utils import add_params
from hyper_params import return_hyperparam_list

# import your solution here
try:
    from matheus import matheus_solution
except Exception as e:
    print(e, "in matheus file")
try:
    from ham import ham_solution
except Exception as e:
    print(e, "in ham file")
try:
    from sean import sean_solution
except Exception as e:
    print(e, "in sean file")


def read_file(input_location):
    """
    Return info from the input_location.

    Parameters
    ---------
    input_location : str
        Full path to input location.

    Returns
    -------
    None

    """
    with open(input_location, 'r') as f:
        # TODO these should read the correct stuff
        A, B = line_to_data(f.readline(), np_array=False, dtype=int)
        C = line_to_data(f.readline(), dtype=float)
        info = (A, B, C)
    return info


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
    with open(output_location, 'w') as f:
        # TODO update with writing the correct stuff
        f.write("{}\n".format(len(solution)))
        for val in solution:
            f.write("{} ".format(int(val)))


def print_solution(solution):
    """
    Print things relevant to the solution.

    For example, you could print the number of taxis with no rides.
    Or the max number of rides assigned to a taxi.
    """
    # TODO print actually useful things, like summary information.
    print("\tSolution is: {}".format(solution))


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
    info = read_file(input_location)
    solution, score = method(info, **kwargs)
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
    individual_list_size = (
        (len(filenames) + len(parameter_list) + len(skip)) / 3)
    if (individual_list_size != len(filenames)):
        raise ValueError(
            "Pass equal len filenames {} parameters {} and skips {}".format(
                len(filenames), len(parameter_list), len(skip)))

    # Do setup of arrays etc.
    here = os.path.dirname(os.path.realpath(__file__))
    np.random.seed(seed)  # to reproduce results
    in_dir = "input_files"
    locations = [os.path.join(here, in_dir, filename)
                 for filename in filenames]
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
        for i, (input_location, params) in enumerate(
                zip(locations, parameter_list)):

            # Ignore some files optionally
            if skip[i]:
                print("Skipping {}".format(input_location))
                continue

            # Setup and print what is happening
            print("Working on {} with parameters {} using {}:".format(
                os.path.basename(input_location), params, method.__name__))
            output_location = os.path.join(
                out_dir,
                os.path.basename(input_location[:-3]) + ".out")

            # TODO Put anything which may be useful to all solutions here
            params_copy = copy(params)
            params_copy["output_dir"] = out_dir
            params_copy["input_name"] = os.path.basename(input_location)

            # Actual running happens here
            score = run(input_location, output_location, method, **params_copy)

            # Write the achieved score to disk
            scores[i] = score
            f.write("{} {}\n".format(
                os.path.basename(input_location)[:-3], score))

        # Prints the final score
        last_str = "Total score: {}".format(np.sum(scores))
        f.write(last_str)
        print(last_str)


def setup_params():
    """
    Here you can set up specific parameters for each file in filenames.

    The output format should be a list of dictionaries. 
    You can either manually make this list of dictionaries
    or use the helper function add_params which can be seen in use
    in the default version of this function.

    """
    # At the very least you must return this from the function,
    # A list of blank dictionaries.
    param_list = [{}, {}, {}, {}, {}]

    # This holds which iteration of the main loop you are on
    # Can be useful to know in some circumstances.
    param_list = add_params(param_list, "iter", [
                            str(i + 1) for i in range(len(filenames))])

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
    method = sean_solution

    # TODO change this to be the actual filenames
    filenames = ["x.in", "y.in", "z.in", "w.in", "u.in"]

    # TODO Indicate which files to run
    skip = [False, False, False, False, False]

    # TODO Set the random seed for reproducibility
    seed = 1

    # TODO inside of setup_params you can change parameters for specific files.
    param_list = setup_params()

    main(method, filenames, param_list, skip, seed)
