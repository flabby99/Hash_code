import os
import time
import itertools
import operator

from sklearn.feature_extraction.text import TfidfVectorizer

# In case doing hyperparam opt
try:
    from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, space_eval
except:
    pass

from utils import save_object
from common import scorer
from matheus import count_ingredients


class Pizza:
    """
    These is a template for a general class with some
    things which can be useful.
    """

    def __init__(self, ingredients, idx, score):
        self.score = score
        self.idx = idx
        self.ingredients = ingredients
        self.used = False

    def to_string(self):
        return " ".join(['"{}"'.format(v) for v in self.ingredients])

    def cs_similarity(self, distance_mat):
        row = distance_mat.getrow(self.idx).toarray().flatten()
        return distance_mat.dot(row)

    def find_matches(self, distance_mat, vectoriser, pizza_list, num_choices):
        choices = [self]
        idxs = []
        for _ in range(num_choices - 1):
            pizza = " ".join([p.to_string() for p in choices])
            tf_val = vectoriser.transform([pizza,]).toarray().flatten()
            distances = distance_mat.dot(tf_val)

            best_distance, best_val = 1, -1
            for i, val in enumerate(distances):
                if pizza_list[i].used is False:
                    if val <= best_distance:
                        best_distance = val
                        best_val = i
                    if best_distance == 0:
                        break

            choices.append(pizza_list[best_val])
            pizza_list[best_val].used = True
            idxs.append(best_val)

        return choices, idxs


    def __str__(self):
        return "Pizza {} with ingredients {}".format(self.idx, self.ingredients)


def sean_solution(info, **kwargs):
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
    M, T2, T3, T4, pizzas = info

    ing = count_ingredients(pizzas)
    pizza_list = [Pizza(p, i, sum([1 / ing[key] for key in p])) for i, p in enumerate(pizzas)]
    pizza_list = sorted(
        pizza_list, key=operator.attrgetter("score"), reverse=True
    )

    corpus = [p.to_string() for p in pizza_list]

    vectoriser = TfidfVectorizer()
    feature_mat = vectoriser.fit_transform(corpus)

    t_dict = {4: T4, 3: T3, 2: T2}

    def objective(args):
        """Actually write the solution part here."""
        ordering = args.get("ordering", [4, 3, 2])

        choices = []
        total_used = 0
        curr_pizza = 0
        for o in ordering:
            for _ in range(t_dict[o]):
                if total_used + o > M:
                    break
                for val in range(curr_pizza, len(pizza_list)):
                    if pizza_list[val].used is False:
                        curr_pizza = val
                        pizza_list[curr_pizza].used = True
                        break
                matches, idxs = pizza_list[curr_pizza].find_matches(feature_mat, vectoriser, pizza_list, num_choices=o)
                choices.append([o, ] + [m.idx for m in matches])
                total_used += o
                for m in idxs:
                    pizza_list[m].used = True

        solution = choices
        score = scorer(solution, info)

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


def assign_pizzas(sorted_pizzas, draw_arr, info):
    solution = []
    curr_idx = 0
    for val in draw_arr:
        end_idx = curr_idx + val
        if end_idx <= len(sorted_pizzas):
            choices = [n for n in sorted_pizzas[curr_idx:end_idx]]
            team_size = val
            new_entry = [team_size,] + choices
            solution.append(new_entry)
        curr_idx += val

    score = scorer(solution, info)

    return solution, score


def make_draw_arr(total_pizzas, order, size_dict):
    total_used = 0
    draw_arr = []
    for val in order:
        team_size = size_dict[val]
        for i in range(team_size):
            if total_used + val <= total_pizzas:
                draw_arr.append(val)
                total_used += val
            else:
                break
    return draw_arr


def brute_force(info, **kwargs):
    """Brute force best solution - should only be used on the first."""
    M, T2, T3, T4, pizzas = info

    pizza_idxs = [i for i in range(len(pizzas))]

    # Can order as T2 > T3 > T4 and permutes
    teams = [2, 3, 4]
    team_dict = {2: T2, 3: T3, 4: T4}

    total_possible = 0
    best_score = 0

    # team_permutations = 6
    # pizza_permutations = math.factorial(M)
    for team_perm in itertools.permutations(teams):
        draw_arr = make_draw_arr(M, team_perm, team_dict)
        for i, pizza_perm in enumerate(itertools.permutations(pizza_idxs)):
            solution, score = assign_pizzas(pizza_perm, draw_arr, info)
            if score > best_score:
                best_solution = solution
                best_score = score
            total_possible += 1

    print("Tested a total of {} solutions".format(total_possible))
    print("The best solution was {}".format(best_solution))
    return best_solution, best_score
