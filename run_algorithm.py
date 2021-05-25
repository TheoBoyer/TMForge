"""

    run an algorithm in training mode

"""

import argparse

from core.AlgorithmWrapper import AlgorithmWrapper

def run(algo):
    """
        run the given algorithm in training mode
    """

    algo = AlgorithmWrapper(algo)
    algo.runAlgorithm()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Wrapper to run a given algorithm')
    parser.add_argument(
        'algo',
        help='Path to the folder of the algorithm you want to run'
    )

    args = parser.parse_args()
    run(args.algo)