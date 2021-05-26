import json
from package.DQNAgent import DQNAgent

from devices.TMKeyboard import TM_KEYBOARD_ACTIONS

with open('hyperparameters.json') as f:
    hyperparameters = json.load(f)

agent = DQNAgent(len(TM_KEYBOARD_ACTIONS), hyperparameters, "./policy.pt")

def play(state, tmenv):
    return agent.play(state)