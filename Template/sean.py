import os
import time

import numpy as np

# In case doing hyperparam opt
try:
    from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, space_eval
except:
    pass

from utils import save_object

# TODO Put classes here that may be useful to store info in


class General:
    """
    These is a template for a general class with some
    things which can be useful.
    """

    def __init__(self, args, idx):
        self.score = 0
        self.idx = idx

    def __repr__(self):
        return "Thing {} with properties".format(self.idx)


def sean_solution(input_info, **kwargs):
    """
    This solution is designed to be performed as follows:
    1.  Setup anything, such as arrays or sorting.
        Also break down info into components.
    2.  objective can access anything from the main body part.
        As such, pass anything extra which may be needed
        (such as hyper-params) into objective as args (a dict)
        perform the actual solving logic part here.
    3.  At the end, can search over hyper-paramters (the args)
        That are passed into objective.
        However, if doing a simple function, this part
        can be safely ignored.

    """
    # TODO main body part here - especially setup

    def objective(args):
        """Actually write the solution part here."""
        # TODO Parse out the args if needed
        val = args.get(["name", None])

        # TODO Solve the thing here
        solution = 0
        score = 0

        # Return something flexible that can be used with hyperopt
        # Main point is that it has score and solution.
        return {
            "loss": -score,
            "score": score,
            "solution": solution,
            "eval_time": time.time(),
            "status": STATUS_OK,
        }

    # Ignore this bit if not searching hyper_parameters!
    if kwargs.get("search", True):
        trials = Trials()

        # TODO Setup what values the args searching over can have
        space = hp.choice(
            "args",
            [{"arg1": hp.lognormal("arg1", 1, 0.5), "arg2": hp.uniform("arg2", 1, 10)}],
        )

        # TODO If you know the best you do, pass loss_threshold=-best
        # Do hyper-param searching - possible pass per filename num_evals
        best = fmin(
            objective,
            space=space,
            algo=tpe.suggest,
            max_evals=kwargs.get("num_evals", 10),
            trials=trials,
        )

        # Get the best hyper-params from fmin
        print("Best hyper-parameters found were:", best)
        args = space_eval(space, best)

        # Save the trials to disk
        # These trials can be printed using print_trial_info in utils
        out_name = os.path.join(
            kwargs["output_dir"], "_" + kwargs["input_name"][:-2] + "pkl"
        )
        save_object(trials, out_name)

    else:
        # By default, this is just an empty dictionary.
        args = kwargs.get("objective_args")

    result = objective(args)
    return result["solution"], result["score"]
