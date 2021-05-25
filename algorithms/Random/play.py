from random import randint
import package.veryImportantFile

def play(state, tmenv):
    return randint(0, tmenv.controller.ACTION_SPACE-1)