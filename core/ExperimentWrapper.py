"""
    
    Wrapper for a result of experiment. Load the required functions, and run evaluation episodes

"""

import json
import os
import sys
import config
import time
import numpy as np

from utils.Validation import assertFunctionExist, assertPathExists, keepPathIfExist
from core.MakeTMEnv import MakeTMEnv
from utils.Validation import load_config
from core.Telemetry import Telemetry
from utils.draw import SplittedLayoutWindow


class ExperimentWrapper:
    """
        Wrapper for a result of experiment. Load the required functions, and run evaluation episodes
    """
    def __init__(self, experiment_path):
        self.experiment_path = experiment_path
        self.name = os.path.basename(self.experiment_path)
        # Add the experiment folder to the import paths
        sys.path.append(self.experiment_path)
        # Change current directory to the experiment's
        os.chdir(self.experiment_path) 
        # Get paths of required files
        self.play_script_path = None
        self.loadRequiredFilesPath()
        # Get paths of optionnal files
        self.hyperparameters_path = None
        self.tryLoadOptionnalFilesPath()
        # The user's function
        self.play = None
        # Load the user's functions
        self.loadRequiredFunctions()
        # Load the optionnal dict (hyperparameters.json)
        self.hyperparameters = None
        self.tryLoadOptionnalDict()

        # Attributes for telemetry
        self.telemetry = Telemetry([
            "Duration",
            "FPS",
            "Action Latency",
            "Episode",
            "Env step",
            "Reward",
            "Action"
        ], dump_file_path="evaluation_metrics.csv")
        # Utility to display a window with a splitted layout. The window will be splitted in 4x3 sections. We provide our telemetry so it is used as a data source
        self.ui = SplittedLayoutWindow(self.telemetry, (3, 2))

        # Define a function we will need later
        def seconds2HoursString(x):
            """
                Lambda function to convert a number of seconds in float to a formatted string: hh:mm:ss
            """
            x = round(x)

            h = x // 3600
            m = (x % 3600) // 60
            s = x % 60

            return "{}:{:02d}:{:02d}".format(
                h, m, s
            )
        ## bind the divisions of the window to the corresponding metrics
        # The (0, 0) window will display the duration of the execution of the algorithm
        self.ui.bind(0, "Duration", 'last', {"lambda": seconds2HoursString})
        # The (0, 1) window will display the current "FPS" of the algortihm
        self.ui.bind(1, "FPS", 'last')
        # The (1, 0) window will display the number of episodes
        self.ui.bind(2, "Episode", 'last')
        # The (1, 1) window will display the number of game steps
        self.ui.bind(3, "Env step", 'last')
        # The (2, 0) window will display the number of time the agent finished the map
        self.ui.bind(4, "Reward", 'last')
        # The (2, 1) window will display the last action that the agent took 
        self.ui.bind(5, "Action", 'keyboard')

    def loadRequiredFilesPath(self):
        """
            Complete the paths of the required files or throw an error if it can't find them
        """
        self.experiment_path = assertPathExists(
            ".",
            error_message="{} folder doesn't exists".format(self.experiment_path)
        )
        
        self.play_script_path = assertPathExists(
            self.experiment_path,
            "play.py",
            "{} is an invalid algorithm path because play.py script wasn't found".format(self.experiment_path)
        )

    def tryLoadOptionnalFilesPath(self):
        """
            Complete the paths of the optionnal files if they exists
        """
        self.hyperparameters_path = keepPathIfExist(
            self.experiment_path,
            "hyperparameters.json",
            "hyperparameters.json wasn't found, your script will run with an empty hyperparameters set"
        )

    def loadRequiredFunctions(self):
        """
            Load the user functions (play from play.py) or throw an error if it can't find them
        """
        sys.path.append(self.experiment_path)
        self.play = assertFunctionExist(
            self.play_script_path,
            "play"
        )

    def tryLoadOptionnalDict(self):
        """
            Load the optionnal dictionnaries (hyperparameters.json) if they exists
        """
        if self.hyperparameters_path is not None:
            with open(self.hyperparameters_path) as f:
                self.hyperparameters = json.load(f)
        else:
            self.hyperparameters = {}

    def assertSameConfig(self):
        exp_config = load_config(self.experiment_path)

        actual_config_keys = [v for v in dir(config) if not v.startswith('__')]
        exp_config_keys = [v for v in dir(exp_config) if not v.startswith('__')]

        missing_in_exp = []
        diff = []
        for k in actual_config_keys:
            actual_value = getattr(config, k)
            try:
                exp_value = getattr(exp_config, k)
                if actual_value != exp_value:
                    diff.append((k, actual_value, exp_value))
            except:
                missing_in_exp.append(k)

        missing_in_actual = []
        for k in exp_config_keys:
            try:
                exp_value = getattr(config, k)
            except:
                missing_in_actual.append(k)

        if len(missing_in_exp) + len(diff) + len(missing_in_actual):
            if len(missing_in_exp):
                print("{} is/are missing in the config experiment folder.\n".format(
                    str(missing_in_exp)
                ))

            if len(diff):
                print("Some values are not the same in your experiment config.py and in the current config.py")
                for k, actual_value, exp_value in diff:
                    print("{} is different (Experiment: {} | Actual={}}".format(
                        k, exp_value, actual_value
                    ))

            if len(missing_in_actual):
                print("{} is/are missing in the current config.py\n".format(
                    str(missing_in_exp)
                ))

            raise ValueError("It could cause undetermined behaviour. If you still want to evaluate this experiment, modify the current config.py or the one of your experiment folder")

    def update(self):
        """
            Here are the function to perform each step that takes time. It's wrapped in this function so it can be called during the waiting phase of the environment
        """
        if not self.ui.draw():
            raise Exception("Graphic mode Interuption")

    def test(self, n_episodes=10):
        """
            Run "n_episodes" evaluation episodes on the results of the experiment
        """
        self.assertSameConfig()
        with MakeTMEnv(manual_override=False) as tmenv:
            self.tstart = time.time()
            tmenv.attachToWaitHook(self.update)
            for i in range(n_episodes):
                state = tmenv.reset()
                total_rewards = 0
                print("Starting episode", i+1)
                s = 0
                while True:
                    s += 1
                    print("State shape:", state.shape, end=" | ")
                    action = self.play(state, tmenv)
                    state, reward, done, info = tmenv.step(action)
                    total_rewards += reward
                    print("Performed action: {} | Obtained reward: {}".format(
                        tmenv.controller.actionToString(info["performed_action"]),
                        reward
                    ))
                    self.telemetry.append({
                        "Duration": time.time() - self.tstart,
                        "FPS": tmenv.getFPS(),
                        "Action Latency": info["action_latency"],
                        "Episode": i,
                        "Env step": s,
                        "Reward": reward,
                        "Action": info["performed_action"],
                    })

                    if done:
                        break

                print("Finished ! Obtained {} rewards".format(total_rewards))