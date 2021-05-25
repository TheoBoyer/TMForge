import os

from random import randint
from core.MakeTMEnv import MakeTMEnv
import package.veryImportantFile

def run(hyperparameters):
    f = open("file", "w")
    f.write("This for example is a model file")
    f.close()
    with MakeTMEnv() as tmenv:
        state = tmenv.reset()
        for t in range(100):
            print("State shape:", state.shape, end=" | ")
            action = randint(0, tmenv.controller.ACTION_SPACE-1)
            state, reward, done, info = tmenv.step(action)
            print("Performed action: {} | Obtained reward: {}".format(
                tmenv.controller.actionToString(info["performed_action"]),
                reward
            ))
            if done:
                print("Episode finished after {} steps".format(t+1))
                break