import torch
import torch.nn as nn
import torch.nn.functional as Func

if torch.cuda.is_available():  
    dev = "cuda:0" 
else:  
    dev = "cpu"
device = torch.device(dev)

import config
import numpy as np
from package.DQN import DQN
from copy import deepcopy
from random import random, randint


class DQNAgent:
    def __init__(self, n_actions, hyperparameters, source_file=None, model_save_path="."):
        self.hyperparameters = hyperparameters
        self.model_save_path = model_save_path
        self.n_actions = n_actions

        if source_file is None:
            self.policy = DQN(config.CAPTURE_IMG_HEIGHT, config.CAPTURE_IMG_WIDTH, n_actions).to(device)
        else:
            self.policy = torch.load(source_file).to(device)
        self.target = DQN(config.CAPTURE_IMG_HEIGHT, config.CAPTURE_IMG_WIDTH, n_actions).to(device)
        self.target.load_state_dict(self.policy.state_dict())
        self.target.eval()

        self.optimizer = torch.optim.RMSprop(self.policy.parameters(), lr=hyperparameters["learning_rate"])
        self.n_steps = 0
        self.epsilon = hyperparameters["initial_epsilon"]
        self.last_q_value = 0

    def getTrainSteps(self):
        return self.n_steps
    
    def getEpsilon(self):
        return self.epsilon

    def getLastQValue(self):
        return self.last_q_value

    def play(self, state):
        state = self.preprocess(state)
        qs = self.policy(state).squeeze(0).detach().cpu().numpy()
        self.last_q_value = np.max(qs)
        action = np.argmax(qs)
        del qs, state

        if random() < self.epsilon:
            action = randint(0, self.n_actions - 1)
            
        self.epsilon = self.hyperparameters["min_epsilon"] + (self.epsilon - self.hyperparameters["min_epsilon"]) * self.hyperparameters["epsilon_discount_factor"]
        return action

    def preprocess(self, x):
        x = x.mean(-1)
        x = torch.tensor(x, device=device, dtype=torch.float) / 255
        if len(x.shape) < 4:
            x = x.unsqueeze(0)
        return x

    def train_step(self, states, actions, rewards, dones):
        if len(states) < max(self.hyperparameters["min_buff_size"], self.hyperparameters["batch_size"]):
            return
        idxs = np.random.randint(0, len(states) - 1, self.hyperparameters["batch_size"])

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

        s = np.stack(s, axis=0)
        sprime = np.stack(sprime, axis=0)
        a = np.expand_dims(np.array(a), axis=-1)
        r = np.array(r)
        d = np.array(d)

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

        q_t_prime[d] = 0

        q_t_estim = r + (q_t_prime * self.hyperparameters["reward_discount_factor"])

        criterion = nn.SmoothL1Loss()
        loss = criterion(q_t, q_t_estim.unsqueeze(1))

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.n_steps += 1

        if self.n_steps % self.hyperparameters["target_frequency_update"] == 0:
            torch.save(deepcopy(self.policy).cpu(), self.model_save_path + "/target.pt")
            print("Updating target...")
            self.target.load_state_dict(self.policy.state_dict())

        del a, r, q_t, q_t_prime, q_t_estim

    def getState(self):
        torch.save(deepcopy(self.policy).cpu(), self.model_save_path + "/policy.pt")
        return {
            "policy_model": self.model_save_path + "/policy.pt",
            "target_model": self.model_save_path + "/target.pt",
            "n_steps": self.n_steps,
            "epsilon": self.epsilon
        }