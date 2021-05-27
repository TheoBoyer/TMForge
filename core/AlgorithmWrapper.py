"""
    
    Wrapper for a user's algorithm. Load the required functions, create the experiment folder, copy everything into it, and run the train function

"""

import json
import os
import sys
from shutil import copyfile, copytree

from utils.Validation import assertFunctionExist, assertPathExists, keepPathIfExist
from utils.Folders import getAvailableFolderName

class AlgorithmWrapper:
    """
        Wrapper for a user's algorithm. Load the required functions, create the experiment folder, copy everything into it, and run the train function
    """
    def __init__(self, algo_path):
        self.algo_path = algo_path
        self.name = os.path.basename(self.algo_path)
        self.experiment_folder = os.path.abspath("./experiments/")
        # Get paths of required files
        self.play_script_path = None
        self.train_script_path = None
        self.loadRequiredFilesPath()
        # Get paths of optionnal files
        self.hyperparameters_path = None
        self.tryLoadOptionnalFilesPath()
        # Load the optionnal dict
        self.hyperparameters = None
        self.tryLoadOptionnalDict()

        self.train = None
        self.play = None        
        

    def loadRequiredFilesPath(self):
        """
            Complete the paths of the required files or throw an error if it can't find them
        """
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
        """
            Complete the paths of the optionnal files if they exists
        """
        self.hyperparameters_path = keepPathIfExist(
            self.algo_path,
            "hyperparameters.json",
            "hyperparameters.json wasn't found, your script will run with an empty hyperparameters set"
        )

    def loadRequiredFunctions(self):
        """
            Load the user functions (run from train.py and play from play.py) or throw an error if it can't find them
        """
        self.train = assertFunctionExist(
            "./train.py",
            "run"
        )

        self.play = assertFunctionExist(
            "./play.py",
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

    def runAlgorithm(self):
        """
            Create the experiment folder, copy the code, and call the user's train function
        """
        # Get a unique name for this experiment
        self.experiment_path = getAvailableFolderName(self.experiment_folder, self.name)
        print("Experiment path:", self.experiment_path)
        # Copy the code and the global config
        copytree(self.algo_path, self.experiment_path)
        copyfile("./config.py", os.path.join(self.experiment_path, "config.py"))
        # Add the experiment folder to the import paths
        sys.path.append(self.experiment_path)
        # Change current directory to the experiment's
        os.chdir(self.experiment_path) 
        # Load the user's functions
        self.loadRequiredFunctions()
        # Call the user's train function
        self.train(self.hyperparameters)