from algorithms.DQN.package.DQNWrapper import DQNWrapper
import os

from core.MakeTMEnv import MakeTMEnv

def run(hyperparameters):
    with MakeTMEnv() as tmenv:
        dqnWrapper = DQNWrapper(tmenv.controller.ACTION_SPACE, hyperparameters)
        dqnWrapper.run(tmenv)