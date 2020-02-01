# Use this to test something in particular
from time import time

from solution import print_solution
from sean import sean_solution


def test_method(method, info, **kwargs):
    """Can be used to test a method with particular values."""
    start_time = time()
    solution = method(info, **kwargs)
    print("\tCompleted in {} seconds".format(time() - start_time))
    print_solution(solution)


def objective(args):
    case, val = args
    if case == 'case 1':
        return val
    else:
        return val ** 2


def test_opt():
    from hyperopt import hp
    space = hp.choice(
        'a', [
            ('case 1', 1 + hp.lognormal('c1', 0, 1)),
            ('case 2', hp.uniform('c2', -10, 10))
        ])

    from hyperopt import fmin, tpe, space_eval
    best = fmin(objective, space, algo=tpe.suggest, max_evals=100)

    print(best)
    print(space_eval(space, best))
    print(objective(space_eval(space, best)))


if __name__ == "__main__":
    # info = []
    # test_method(sean_solution, info)
    test_opt()
