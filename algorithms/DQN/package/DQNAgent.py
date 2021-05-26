"""

    Agent Wrapper for the DQN algortihm. Handle the model and training of the agent
    The complete algorithm is described here: https://arxiv.org/pdf/1312.5602.pdf

"""

import torch
import torch.nn as nn
import torch.nn.functional as Func

# Use the GPU if possible
if torch.cuda.is_available():  
    dev = "cuda:0" 
else:  
    dev = "cpu"
device = torch.device(dev)

import config
import numpy as np
# Here you can also import from the package folder
from package.DQN import DQN
from copy import deepcopy
from random import random, randint


class DQNAgent:
    """
        Agent Wrapper for the DQN algortihm. Handle the model and training of the agent
    """
    def __init__(self, n_actions, hyperparameters, source_file=None, model_save_path="."):
        self.hyperparameters = hyperparameters
        self.model_save_path = model_save_path
        self.n_actions = n_actions
        # Create a new model or load if a source file is provided
        if source_file is None:
            self.policy = DQN(config.CAPTURE_IMG_HEIGHT, config.CAPTURE_IMG_WIDTH, n_actions).to(device)
        else:
            self.policy = torch.load(source_file).to(device)
        # Target network
        self.target = DQN(config.CAPTURE_IMG_HEIGHT, config.CAPTURE_IMG_WIDTH, n_actions).to(device)
        self.target.load_state_dict(self.policy.state_dict())
        self.target.eval()
        # Use of RMSprop. I've read that RMSprop can be more stable than Adam in non-stationary optimization problems
        self.optimizer = torch.optim.RMSprop(self.policy.parameters(), lr=hyperparameters["learning_rate"])
        self.n_steps = 0
        self.epsilon = hyperparameters["initial_epsilon"]
        self.last_q_value = 0

    def evalMode(self):
        """
            Switch the agent into evaluation mode
        """
        self.epsilon = 0.02

    def getTrainSteps(self):
        """
            Return the number of training steps performed
        """
        return self.n_steps
    
    def getEpsilon(self):
        """
            Return the epsilon aka the probability of the agent selecting a random action
        """
        return self.epsilon

    def getLastQValue(self):
        """
            Return the Q value of the state given in the last call of "play"
        """
        return self.last_q_value

    def play(self, state):
        """
            Select an action based on the given state.
        """

        ### Disclaimer: We want to make a forward pass of the network even if the final action taken is random ON PURPOSE. Two reasons:
        ###     1. We can have an estimation of the Q-value regardless of how the action was choosed
        ###     2. This portion of the code execute itself after the obtention of the state, and before the choosen action os performed.
        ###        As a consequence, doing a forward pass every time bring stability in the latency between obtention of the state and commitment of the action.

        # Processing Image + pytorch tensor conversion
        state = self.preprocess(state)
        # Predict the estimated Q-value in a numpy array
        qs = self.policy(state).squeeze(0).detach().cpu().numpy()
        # Take the best action
        action = np.argmax(qs)
        del state

        # Take the best action
        if random() < self.epsilon:
            action = randint(0, self.n_actions - 1)

        # Save current the Q-value
        self.last_q_value = qs[action]
        # Update epsilon following the exponential schedule
        self.epsilon = self.hyperparameters["min_epsilon"] + (self.epsilon - self.hyperparameters["min_epsilon"]) * self.hyperparameters["epsilon_discount_factor"]
        return action

    def preprocess(self, x):
        """
            Prepare the raw states for a DQN forward pass
        """
        # Turn into a grayscale
        x = x.mean(-1)
        # Turn Normalize the values
        x = torch.tensor(x, device=device, dtype=torch.float) / 255
        # Assert that the batch dimension is respected
        if len(x.shape) < 4:
            x = x.unsqueeze(0)
        return x

    def train_step(self, states, actions, rewards, dones):
        """
            Perform a training step using the given replay buffer
        """
        # We want to train only if we have enough data and respecting the "min_buff_size" hyperparameter
        if len(states) < max(self.hyperparameters["min_buff_size"], self.hyperparameters["batch_size"]):
            return
        # Sample from the replay buffer
        idxs = np.random.randint(0, len(states) - 1, self.hyperparameters["batch_size"])
        # Gather the data of the batch
        s = []
        sprime = []
        a = []
        r = []
        d = []
        for i in idxs:
            s.append(states[i])
            sprime.append(states[i+1])
            a.append(actions[i])
            r.append(rewards[i])
            d.append(dones[i])

        # List to numpy array / stacking
        s = np.stack(s, axis=0)
        sprime = np.stack(sprime, axis=0)
        a = np.expand_dims(np.array(a), axis=-1)
        r = np.array(r)
        d = np.array(d)

        # Preprocess the batch + to pytorch tensors
        s = self.preprocess(s)
        sprime = self.preprocess(sprime)
        a = torch.tensor(a, dtype=torch.long, device=device)
        r = torch.tensor(r, dtype=torch.float, device=device)

        q_t = self.policy(s).gather(1, a)

        #Classic Q-Learning
        #q_t_prime = self.target(sprime).max(1)[0].detach()

        # Double Q_learning
        self.policy.eval()
        aprime = self.policy(sprime).max(1)[1].detach().unsqueeze(-1)
        self.policy.train()
        q_t_prime = self.target(sprime).gather(1, aprime).squeeze(-1)
        # The Q' estimation is 0 if the state was terminal
        q_t_prime[d] = 0

        # Calculate the final estimation of the Q-value
        q_t_estim = r + (q_t_prime * self.hyperparameters["reward_discount_factor"])

        # Huber Loss variant
        criterion = nn.SmoothL1Loss()
        loss = criterion(q_t, q_t_estim.unsqueeze(1))
        # Perform the gradient descent
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.n_steps += 1
        # Update the target and backup when it's time to
        if self.n_steps % self.hyperparameters["target_frequency_update"] == 0:
            torch.save(deepcopy(self.policy).cpu(), self.model_save_path + "/target.pt")
            print("Updating target...")
            self.target.load_state_dict(self.policy.state_dict())

        # Memory management
        del a, r, q_t, q_t_prime, q_t_estim

    def getState(self):
        """
            Return the internal state of the wrapper for backup 
        """
        torch.save(deepcopy(self.policy).cpu(), self.model_save_path + "/policy.pt")
        return {
            "policy_model": self.model_save_path + "/policy.pt",
            "target_model": self.model_save_path + "/target.pt",
            "n_steps": self.n_steps,
            "epsilon": self.epsilon
        }