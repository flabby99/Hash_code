"""
This file contains various utility functions.
You can add extra utilities here, but generally you should
not need to know how the existing functions work.
"""

import pickle
import zipfile
import os

import numpy as np


def line_to_data(line, np_array=True, dtype=int):
    """
    Return an array of data with each value being of type dtype.
    The values are extracted from line, which is separated by spaces by default.
    if np_array is true, returns a numpy array, otherwise returns a python List.
    """
    if np_array:
        return np.fromstring(line.strip("\n"), dtype=dtype, sep=" ")
    else:
        to_return = [dtype(x) for x in line.strip("\n").split(" ")]
        if len(to_return) == 1:
            return to_return[0]
        else:
            return to_return


def zip_dir(in_dir, out_loc, ext=None):
    """
    Zip up in_dir to out_loc, optionally only taking files with given ext.
    """
    zipf = zipfile.ZipFile(out_loc, "w", zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(in_dir):
        for f in files:
            if ext is not None:
                if os.path.splitext(f)[-1] == ext:
                    zipf.write(
                        os.path.join(root, f),
                        os.path.relpath(os.path.join(root, f), in_dir),
                    )
            else:
                zipf.write(
                    os.path.join(root, f),
                    os.path.relpath(os.path.join(root, f), in_dir),
                )
    zipf.close()
    print("Wrote zip file with source code to {}".format(out_loc))

def print_trial_info(in_dir):
    """Print hyperopt.Trials() info loaded via pickle."""
    for f in os.listdir(in_dir):
        if f[-3:] == "pkl":
            with open(os.path.join(in_dir, f), "rb") as inp:
                trial = pickle.load(inp)
                print("For {}:".format(f))
                for d, l in zip(trial.trials, trial.losses()):
                    print("\t{}: Loss {}".format(d["misc"]["vals"], l))


def save_object(obj, out_name):
    """Save obj to out_name using pickle."""
    with open(out_name, "wb") as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def add_params(l, name, values):
    """
    Add values to l with key=name.
    If values is one value, add the same value each time.
    """
    if type(values) != list:
        values = [values] * len(l)
    if len(l) != len(values):
        raise ValueError(
            "Unequal length lists in add_params {} {}".format(len(l), len(values))
        )
    for i, val in enumerate(values):
        l[i][name] = val
    return l


if __name__ == "__main__":
    """Can be run here to look at Trial data."""
    here = os.path.dirname(os.path.realpath(__file__))
    dirname = "00-14-11"
    main_in_dir = os.path.join(here, "outputs", dirname)
    print_trial_info(main_in_dir)
