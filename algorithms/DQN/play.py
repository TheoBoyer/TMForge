import json
import os
from random import randint
from package.DQNAgent import DQNAgent

from devices.TMKeyboard import TM_KEYBOARD_ACTIONS

with open('hyperparameters.json') as f:
    hyperparameters = json.load(f)

if os.path.isfile("./policy.pt"):
    agent = DQNAgent(len(TM_KEYBOARD_ACTIONS), hyperparameters, "./policy.pt")
else:
    agent = None
def play(state, tmenv):
    if agent is not None:
        return agent.play(state)
    return randint(0, tmenv.controller.ACTION_SPACE-1)