import numpy as np
import config
import time
import json

from collections import deque
from package.DQNAgent import DQNAgent
from core.Telemetry import Telemetry
from utils.draw import SplittedLayoutWindow

EPISODE_SAVE_FREQUENCY = 20

class DQNWrapper:
    def __init__(self, n_actions, hyperparameters, source_file=None):
        self.hyperparameters = hyperparameters
        self.agent = DQNAgent(n_actions, hyperparameters)
        self.game_steps = 0
        self.tstart = time.time()
        self.n_finish = 0
        self.n_episode = 0

        self.frames = deque(maxlen=self.hyperparameters["buffer_size"])
        self.actions = deque(maxlen=self.hyperparameters["buffer_size"])
        self.rewards = deque(maxlen=self.hyperparameters["buffer_size"])
        self.dones = deque(maxlen=self.hyperparameters["buffer_size"])

        self.telemetry = Telemetry([
            "Duration",
            "FPS",
            "Action Latency",
            "Episode",
            "Env step",
            "Train step",
            "Finish",
            "Reward",
            "Q-value",
            "Epsilon",
            "Action",
            "Episode Reward"
        ])

        self.ui = SplittedLayoutWindow(self.telemetry, (4, 3))

        def seconds2HoursString(x):
            x = round(x)

            h = x // 3600
            m = (x % 3600) // 60
            s = x % 60

            return "{}:{:02d}:{:02d}".format(
                h, m, s
            )

        self.ui.bind(0, "Duration", 'last', {"lambda": seconds2HoursString})
        self.ui.bind(1, "FPS", 'last')
        self.ui.bind(2, "Episode", 'last')
        self.ui.bind(3, "Env step", 'last')
        self.ui.bind(4, "Train step", 'last')
        self.ui.bind(5, "Finish", 'last')
        self.ui.bind(6, "Reward", 'last')
        self.ui.bind(7, "Q-value", 'last', {"pattern": "{:.4f}"})
        self.ui.bind(8, "Epsilon", 'last', {"pattern": "{:.4f}"})
        self.ui.bind(9, "Action", 'keyboard')
        self.ui.bind(10, "Q-value", 'graphic', {"maxlen": 30, "approx_type": 'last'})
        self.ui.bind(11, "Episode Reward", 'graphic', {"maxlen": 30, "approx_type": 'moving_average'})

    def getState(self):
        frames_path = "frames_buffer.npy"
        actions_path = "actions_buffer.npy"
        rewards_path = "rewards_buffer.npy"
        dones_path = "dones_buffer.npy"
        np.save(frames_path, np.array(self.frames))
        np.save(actions_path, np.array(self.actions))
        np.save(rewards_path, np.array(self.rewards))
        np.save(dones_path, np.array(self.dones))
        return {
            "agent": self.agent.getState(),
            "telemetry": self.telemetry.getState(),
            "game_steps": self.game_steps,
            "duration": time.time() - self.tstart,
            "n_finish": self.n_finish,
            "n_episode": self.n_episode,
            "frames": frames_path,
            "actions": actions_path,
            "rewards": rewards_path,
            "dones": dones_path,
        }
    
    def saveState(self):
        with open('state_backup.json', 'w') as f:
            json.dump(self.getState(), f)

    def update(self):
        if self.game_steps % self.hyperparameters["train_every"] == 0:
            self.agent.train_step(self.frames, self.actions, self.rewards, self.dones)
        if not self.ui.draw():
            raise Exception("Graphic mode Interuption")

    def run(self, tmenv):
        self.tstart = time.time()
        tmenv.attachToWaitHook(self.update)
        for i in range(self.hyperparameters["n_episodes"]):
            print("Starting new episode")
            state = tmenv.reset()
            self.total_rewards = 0
            self.n_episode += 1

            while True:
                self.game_steps += 1

                action = self.agent.play(state)
                state, reward, done, info = tmenv.step(action)
                performed_action = info["performed_action"]

                if info["is_finished"]:
                    self.n_finish += 1

                self.frames.append(state)
                self.actions.append(performed_action)
                self.rewards.append(reward)
                self.dones.append(done)
                self.total_rewards += reward

                self.telemetry.append({
                    "Duration": time.time() - self.tstart,
                    "FPS": tmenv.getFPS(),
                    "Action Latency": info["action_latency"],
                    "Episode": self.n_episode,
                    "Env step": self.game_steps,
                    "Train step": self.agent.getTrainSteps(),
                    "Finish": self.n_finish,
                    "Reward": reward,
                    "Q-value": self.agent.getLastQValue(),
                    "Epsilon": self.agent.getEpsilon(),
                    "Action": performed_action,
                    "Episode Reward": self.total_rewards if done else np.NaN
                })
                
                print("Performed action: {} | Obtained reward: {}".format(
                    tmenv.controller.actionToString(performed_action),
                    reward
                ))

                if done:
                    break

            if self.n_episode % EPISODE_SAVE_FREQUENCY == 0:
                print("Making state backup")
                self.saveState()
            
            print("Finished ! Obtained {} rewards".format(self.total_rewards))
