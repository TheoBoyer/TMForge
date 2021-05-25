from random import randint
from core.MakeTMEnv import MakeTMEnv

def run():
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

if __name__ == "__main__":
    run()