"""
    Dummy agent to understand how to use the tool

    This is the "play.py" file. It will be used to test your agent after training.
    You can write anything you want in here. The entry point will be the "play" function.
"""

from random import randint
# Here you can import from the core module of TMForge
# And from your "package" folder
import package.veryImportantFile

# The play function will be called in your "play.py" file at each step of the evaluation episodes.
# The provided state is the same as if you called step on tmenv so it will be a numpy array
def play(state, tmenv):
    return randint(0, tmenv.controller.ACTION_SPACE-1)