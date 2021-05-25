"""

    DQN algortihm. Train an agent on a given trackmania map
    The DQN algorithm is described here: https://arxiv.org/pdf/1312.5602.pdf

"""

# You're able to import files from my package folder
from algorithms.DQN.package.DQNWrapper import DQNWrapper
import os
# But also from the core module
from core.MakeTMEnv import MakeTMEnv

def run(hyperparameters):
    # Creation of the environment
    with MakeTMEnv() as tmenv:
        dqnWrapper = DQNWrapper(tmenv.controller.ACTION_SPACE, hyperparameters)
        # Run the algorithm
        dqnWrapper.run(tmenv)