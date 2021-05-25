import json
import os
import sys
from shutil import copyfile, copytree

from utils.Validation import assertFunctionExist, assertPathExists, keepPathIfExist
from utils.Folders import getAvailableFolderName
from core.MakeTMEnv import MakeTMEnv

class ExperimentWrapper:
    def __init__(self, experiment_path):
        self.experiment_path = experiment_path
        self.name = os.path.basename(self.experiment_path)
        self.play_script_path = None
        self.loadRequiredFilesPath()

        self.hyperparameters_path = None
        self.tryLoadOptionnalFilesPath()

        self.play = None
        self.loadRequiredFunctions()
        
        self.hyperparameters = None
        self.tryLoadOptionnalDict()

    def loadRequiredFilesPath(self):
        self.experiment_path = assertPathExists(
            self.experiment_path,
            error_message="{} folder doesn't exists".format(self.experiment_path)
        )
        
        self.play_script_path = assertPathExists(
            self.experiment_path,
            "play.py",
            "{} is an invalid algorithm path because play.py script wasn't found".format(self.experiment_path)
        )

    def tryLoadOptionnalFilesPath(self):
        self.hyperparameters_path = keepPathIfExist(
            self.experiment_path,
            "hyperparameters.json",
            "hyperparameters.json wasn't found, your script will run with an empty hyperparameters set"
        )

    def loadRequiredFunctions(self):
        sys.path.append(self.experiment_path)
        self.play = assertFunctionExist(
            self.play_script_path,
            "play"
        )

    def tryLoadOptionnalDict(self):
        if self.hyperparameters_path is not None:
            with open(self.hyperparameters_path) as f:
                self.hyperparameters = json.load(f)
        else:
            self.hyperparameters = {}


    def test(self, n_episodes=1):
        with MakeTMEnv() as tmenv:
            for i in range(n_episodes):
                state = tmenv.reset()
                total_rewards = 0
                print("Starting episode", i+1)
                while True:
                    print("State shape:", state.shape, end=" | ")
                    action = self.play(state, tmenv)
                    state, reward, done, info = tmenv.step(action)
                    total_rewards += reward
                    print("Performed action: {} | Obtained reward: {}".format(
                        tmenv.controller.actionToString(info["performed_action"]),
                        reward
                    ))
                    if done:
                        break
                print("Finished ! Obtained {} rewards".format(total_rewards))