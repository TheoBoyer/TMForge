import argparse

from core.ExperimentWrapper import ExperimentWrapper

def run(experiment_path):
    experiment = ExperimentWrapper(experiment_path)
    experiment.test()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Wrapper to run a given algorithm')
    parser.add_argument(
        'experiment',
        help='Path to the folder of the experiment you want to test'
    )

    args = parser.parse_args()
    run(args.experiment)