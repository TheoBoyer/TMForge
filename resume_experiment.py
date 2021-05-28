"""

    Resume the training of an experiment

"""

import argparse

from core.ExperimentWrapper import ExperimentWrapper

def run(experiment_path):
    """
        Resume the training of an experiment
    """
    experiment = ExperimentWrapper(experiment_path)
    experiment.resume()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Wrapper to continue a given experiment')
    parser.add_argument(
        'experiment',
        help='Path to the folder of the experiment you want to resume'
    )

    args = parser.parse_args()
    run(args.experiment)