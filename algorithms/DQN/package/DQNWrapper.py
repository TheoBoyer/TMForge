"""

    Wrapper for the DQN algortihm. Handle the replay buffer and the metrics.
    The complete algorithm is described here: https://arxiv.org/pdf/1312.5602.pdf

"""

import numpy as np
import config
import time
import json
import os

from collections import deque
# Here you can also import from the package folder
from package.DQNAgent import DQNAgent
# And from the core of the library
from core.Telemetry import Telemetry
# And also utility functions
from utils.draw import SplittedLayoutWindow

EPISODE_SAVE_FREQUENCY = 50

class DQNWrapper:
    """
        Wrapper for the DQN algortihm. Handle the replay buffer and the metrics.
    """
    def __init__(self, n_actions, hyperparameters, source_file=None):
        self.hyperparameters = hyperparameters
        self.agent = DQNAgent(n_actions, hyperparameters)
        self.game_steps = 0
        self.tstart = time.time()
        self.initial_duration = 0
        self.n_finish = 0
        self.n_episode = 0
        # Replay buffer
        self.frames = deque(maxlen=self.hyperparameters["buffer_size"])
        self.actions = deque(maxlen=self.hyperparameters["buffer_size"])
        self.rewards = deque(maxlen=self.hyperparameters["buffer_size"])
        self.dones = deque(maxlen=self.hyperparameters["buffer_size"])
        # Metrics to Track and/or display
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
        # Utility to display a window with a splitted layout. The window will be splitted in 4x3 sections. We provide our telemetry so it is used as a data source
        self.ui = SplittedLayoutWindow(self.telemetry, (4, 3))
        # Define a function we will need later
        def seconds2HoursString(x):
            """
                Lambda function to convert a number of seconds in float to a formatted string: hh:mm:ss
            """
            x = round(x)

            h = x // 3600
            m = (x % 3600) // 60
            s = x % 60

            return "{}:{:02d}:{:02d}".format(
                h, m, s
            )
        ## bind the divisions of the window to the corresponding metrics
        # The (0, 0) window will display the duration of the execution of the algorithm
        self.ui.bind(0, "Duration", 'last', {"lambda": seconds2HoursString})
        # The (0, 1) window will display the current "FPS" of the algortihm
        self.ui.bind(1, "FPS", 'last')
        # The (0, 2) window will display the number of episodes
        self.ui.bind(2, "Episode", 'last')
        # The (1, 0) window will display the number of game steps
        self.ui.bind(3, "Env step", 'last')
        # The (1, 1) window will display the number of training steps
        self.ui.bind(4, "Train step", 'last')
        # The (1, 2) window will display the number of time the agent finished the map
        self.ui.bind(5, "Finish", 'last')
        # The (2, 0) window will display the last obtained reward
        self.ui.bind(6, "Reward", 'last')
        # The (2, 1) window will display the Q-value of the last seen state
        self.ui.bind(7, "Q-value", 'last', {"pattern": "{:.4f}"})
        # The (2, 2) window will display the epsilon aka the probability of taking a random action
        self.ui.bind(8, "Epsilon", 'last', {"pattern": "{:.4f}"})
        # The (3, 0) window will display the last action that the agent took 
        self.ui.bind(9, "Action", 'keyboard')
        # The (3, 1) window will display the 30 last q values on a plot
        self.ui.bind(10, "Q-value", 'graphic', {"maxlen": 30, "approx_type": 'last'})
        # The (3, 2) window will display the epsiode rewards obtained during training with a moving average smoothing
        self.ui.bind(11, "Episode Reward", 'graphic', {"maxlen": 30, "approx_type": 'moving_average'})

    def backupExists(self):
        return os.path.isfile('./actions_buffer.npy')

    def loadBackup(self):
        with open('./state_backup.json') as f:
            state = json.load(f)
        
        self.agent.setState(state['agent'])
        self.telemetry.setState(state['telemetry'])

        self.game_steps = state["game_steps"]
        self.initial_duration = state["duration"]
        self.n_finish = state["n_finish"]
        self.n_episode = state["n_episode"]

        # Replay buffer
        self.frames = deque(np.load(state["frames"]), maxlen=self.hyperparameters["buffer_size"])
        self.actions = deque(np.load(state["actions"]), maxlen=self.hyperparameters["buffer_size"])
        self.rewards = deque(np.load(state["rewards"]), maxlen=self.hyperparameters["buffer_size"])
        self.dones = deque(np.load(state["dones"]), maxlen=self.hyperparameters["buffer_size"])

    def getState(self):
        """
            Return a dictionnary representing the state of the algorithm. Used for backups
        """
        tstart = time.time()
        frames_path = "frames_buffer.npy"
        actions_path = "actions_buffer.npy"
        rewards_path = "rewards_buffer.npy"
        dones_path = "dones_buffer.npy"

        buffer_tstart = time.time()
        np.save(frames_path, np.stack(self.frames, axis=0))
        np.save(actions_path, np.array(self.actions))
        np.save(rewards_path, np.array(self.rewards))
        np.save(dones_path, np.array(self.dones))
        buffer_saving_time = time.time() - buffer_tstart

        agent_tstart = time.time()
        agent_state = self.agent.getState()
        agent_saving_time = time.time() - agent_tstart

        telemetry_state = self.telemetry.getState()

        state = {
            "agent": agent_state,
            "telemetry": telemetry_state,
            "game_steps": self.game_steps,
            "duration": time.time() - self.tstart + self.initial_duration,
            "n_finish": self.n_finish,
            "n_episode": self.n_episode,
            "frames": frames_path,
            "actions": actions_path,
            "rewards": rewards_path,
            "dones": dones_path,
        }
        
        return state
    
    def saveState(self):
        """
            Save the current state of the algorithm in the "state_backup.json" file.
            Warning: Take a long time if the buffer is big
        """
        with open('state_backup.json', 'w') as f:
            json.dump(self.getState(), f)
        print("Backup complete !")

    def update(self):
        """
            Here are the function to perform each step that takes time. It's wrapped in this function so it can be called during the waiting phase of the environment
        """
        # Training step
        if self.game_steps % self.hyperparameters["train_every"] == 0:
            self.agent.train_step(self.frames, self.actions, self.rewards, self.dones)
        if not self.ui.draw():
            raise Exception("Graphic mode Interuption")

    def run(self, tmenv):
        """
            Run the DQN algorithm.
        """
        with open("debug.txt", 'w') as f:
            f.write("Debug:\n")

        # Save the time at start to keep track of the duration of execution
        self.tstart = time.time()
        # Attach the update function to the hook provided by the environment. This function will be called during the waiting phase
        tmenv.attachToWaitHook(self.update)
        # Episodes loop
        for i in range(self.n_episode, self.hyperparameters["n_episodes"]):
            print("Starting new episode")
            # Reset the environment. Warning: Blocking call
            state = tmenv.reset()
            self.total_rewards = 0
            self.n_episode += 1

            # Steps loop
            while True:
                self.game_steps += 1

                # The agent select an action
                action = self.agent.play(state)
                # Give this action to the enironment so that it can respond with the new state, observed rewards, wether the state is terminal, and a few more informations
                state, reward, done, info = tmenv.step(action)
                # Save the performed action because it can be different from the action the agent took (if a human overridden the agent's action using a physical device)
                performed_action = info["performed_action"]
                # Count the number of times the agent finished the track
                if info["is_finished"]:
                    self.n_finish += 1
                # Save state, action, reward, done in the replay buffer
                self.frames.append(state)
                self.actions.append(performed_action)
                self.rewards.append(reward)
                self.dones.append(done)
                self.total_rewards += reward
                # Update the telemetry with the current values
                self.telemetry.append({
                    "Duration": time.time() - self.tstart + self.initial_duration,
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
                # Some loging to debug
                print("Performed action: {} | Obtained reward: {}".format(
                    tmenv.controller.actionToString(performed_action),
                    reward
                ))

                # If the run is finished
                if done:
                    break

            if self.n_episode % EPISODE_SAVE_FREQUENCY == 0:
                print("Making state backup")
                self.saveState()
            
            # Some loging to debug
            print("Finished ! Obtained {} rewards".format(self.total_rewards))
