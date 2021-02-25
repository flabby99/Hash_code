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

"""
My idea in pseudocode:

1. Score each street as 1 / length + n_cars
2. For each interscetion, weight incoming paths on score st. SUM(w_i) = 1
3. Get D / num_paths
4. Times = Weights * D / n
5. Find y such that min_time * y = 1
6. set Times = Times * y
7. Round times to int
8. if sum(times) > D, subtract from times to make <= D
"""


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


class Street:
    def __init__(self, start, end, name, length):
        self.start = start
        self.end = end
        self.name = name
        self.length = length
        self.score = 0
        self.cars_using = 0

    def calc_score(self, a=100, b=1):
        self.score = ((1 / self.length) * a) + (self.cars_using * b)

    def __str__(self):
        return "Street {} with length {} and cars {} score {}".format(
            self.name, self.length, self.cars_using, self.score
        )


class Intersection:
    def __init__(self, id):
        self.id = id
        self.num_streets = 0
        self.best_times = []
        self.D = 0

    def find_streets_at_intersection(self, street_info, D):
        starting_streets = []

        for street in street_info:
            if street[1] == self.id:
                starting_streets.append(street)

        self.streets = starting_streets
        self.num_streets = len(starting_streets)
        self.max_lights = min(self.num_streets, D)
        self.D = D

    def weight_streets(self, street_dict):
        scores = np.zeros(self.num_streets)
        for i, s in enumerate(self.streets):
            scores[i] = street_dict[s[2]].score
        scores = scores / np.sum(scores)

        self.street_weights = scores

    def find_street_times(self):
        if self.max_lights == self.D:
            return [1,] * self.max_lights

        avg_time = self.D / self.num_streets
        orig_times = self.street_weights * avg_time
        orig_times = orig_times / np.min(orig_times)
        orig_times = np.round(orig_times).astype(np.uint64)
        self.best_times = orig_times

        # best_times = np.copy(orig_times)

        # diff = -1
        # n_iters = 0
        # while diff < 0:
        #     if n_iters > 100000:
        #         raise RuntimeError(
        #             "Iteration limit reached, original times {}, best times {}, duration {}, sum".format(
        #                 orig_times, best_times, self.D, np.sum(best_times)
        #             )
        #         )
        #     n_iters += 1
        #     diff = self.D - np.sum(best_times)
        #     if self.D < 0:
        #         for i in range(diff):
        #             idx = len(best_times) - 1 - i
        #             if best_times[idx] > 1:
        #                 best_times[idx] -= 1

        # self.best_times = best_times

    def __str__(self):
        return "Intersection {} with {} streets and times {}, total duration {}".format(
            self.id, self.num_streets, self.best_times, self.D
        )


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

    D, I, S, V, F, street_info, car_info = input_info

    s_dict = {}
    for s in street_info:
        s_dict[s[2]] = Street(*s)

    # Find busy streets
    for c in car_info:
        paths = c[1:]
        for p in paths:
            s_dict[p].cars_using += 1

    for s in s_dict.values():
        s.calc_score()
        # print(s)

    inter_list = []
    for i in range(I):
        intersection = Intersection(i)
        intersection.find_streets_at_intersection(street_info, D)
        intersection.weight_streets(s_dict)
        intersection.find_street_times()
        inter_list.append(intersection)

    # for I in inter_list:
    #     print(I)

    def objective(args):
        """Actually write the solution part here."""
        # TODO Parse out the args if needed
        val = args.get("name", None)

        # TODO Solve the thing here
        solution = []

        for I in inter_list:
            num_lights = len(I.best_times)
            street_names = [s[2] for s in I.streets]
            line_to_append = [I.id, num_lights]
            idxs = [i for i in range(len(street_names))]
            sorted_idx = [x for x, _ in sorted(zip(idxs, I.best_times), key=lambda pair: pair[1], reverse=True)]
            for i in sorted_idx:
                name = street_names[i]
                time_val = I.best_times[i]
                line_to_append.append((name, time_val))
            solution.append(line_to_append)

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
