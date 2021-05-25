"""
    Dummy agent to understand how to use the tool.

    This is the "train.py" file. It will be used to train your agent.
    You can write anything you want in here. The entry point will be the "run" function.
"""
import os

from random import randint
# Here you can import from the core module of TMForge
from core.MakeTMEnv import MakeTMEnv
# And also from your "package" folder
import package.veryImportantFile

# The run function will be called in your "train.py" file to start the training
def run(hyperparameters):
    # If you write files the will be in the experiment folder
    f = open("file", "w")
    f.write("This for example is a model file")
    f.close()
    # Make the trackmania environment. API is similar to OpenAI's gym: https://gym.openai.com/docs/
    with MakeTMEnv() as tmenv:
        # Reset the trackmania environment
        state = tmenv.reset()
        # Iterate for 100 steps
        for t in range(100):
            # The state is a numpy array containing images according to the config.py file
            print("State shape:", state.shape, end=" | ")
            # The default controller is the keyboard so it's a descrete one. You can choose a random action like so:
            action = randint(0, tmenv.controller.ACTION_SPACE-1)
            # We send our action to the environment. It will send back to us the new state, the obtained reward, wether the state is terminal, and a few more informations
            state, reward, done, info = tmenv.step(action)
            # We display a few things
            print("Performed action: {} | Obtained reward: {}".format(
                # You can access the "performed_action" in the info dictionnary. It can be different than the action you specified if a human use a physical
                # device like a keyboard or a controller. In that case the action of the human will override the one of your agent.
                # You can change this behaviour by specifying manual_override=False when you call MakeTMEnv()
                tmenv.controller.actionToString(info["performed_action"]),
                reward
            ))
            # If the episode is finished we can stop here
            if done:
                print("Episode finished after {} steps".format(t+1))
                break