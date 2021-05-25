import json
import os
import sys
from shutil import copyfile, copytree

from utils.Validation import assertFunctionExist, assertPathExists, keepPathIfExist
from utils.Folders import getAvailableFolderName

class AlgorithmWrapper:
    def __init__(self, algo_path):
        self.algo_path = algo_path
        self.name = os.path.basename(self.algo_path)
        self.experiment_folder = os.path.abspath("./experiments/")
        self.play_script_path = None
        self.train_script_path = None
        self.loadRequiredFilesPath()

        self.hyperparameters_path = None
        self.tryLoadOptionnalFilesPath()

        self.hyperparameters = None
        self.tryLoadOptionnalDict()

        self.train = None
        self.play = None        
        

    def loadRequiredFilesPath(self):
        self.algo_path = assertPathExists(
            self.algo_path,
            error_message="{} folder doesn't exists".format(self.algo_path)
        )
        
        self.play_script_path = assertPathExists(
            self.algo_path,
            "play.py",
            "{} is an invalid algorithm path because play.py script wasn't found".format(self.algo_path)
        )

        self.train_script_path = assertPathExists(
            self.algo_path,
            "train.py",
            "{} is an invalid algorithm path because train.py script wasn't found".format(self.algo_path)
        )

    def tryLoadOptionnalFilesPath(self):
        self.hyperparameters_path = keepPathIfExist(
            self.algo_path,
            "hyperparameters.json",
            "hyperparameters.json wasn't found, your script will run with an empty hyperparameters set"
        )

    def loadRequiredFunctions(self):
        self.train = assertFunctionExist(
            os.path.join(self.experiment_path, "train.py"),
            "run"
        )

        self.play = assertFunctionExist(
            os.path.join(self.experiment_path, "play.py"),
            "play"
        )

    def tryLoadOptionnalDict(self):
        if self.hyperparameters_path is not None:
            with open(self.hyperparameters_path) as f:
                self.hyperparameters = json.load(f)
        else:
            self.hyperparameters = {}

    def runAlgorithm(self):
        self.experiment_path = getAvailableFolderName(self.experiment_folder, self.name)
        print("Experiment path:", self.experiment_path)
        copytree(self.algo_path, self.experiment_path)
        copyfile("./config.py", os.path.join(self.experiment_path, "config.py"))

        sys.path.append(self.experiment_path)

        self.loadRequiredFunctions()
        
        os.chdir(self.experiment_path) 

        self.train(self.hyperparameters)