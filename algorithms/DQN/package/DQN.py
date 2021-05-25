"""

    Pytorch model for the DQN algorithm. Almost Ctrl-C, Ctrl-V from: https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
    The complete algorithm is described here: https://arxiv.org/pdf/1312.5602.pdf

"""
import torch
import torch.nn as nn
import torch.nn.functional as Func

if torch.cuda.is_available():  
    dev = "cuda:0" 
else:  
    dev = "cpu"
device = torch.device(dev)

import config

class DQN(nn.Module):
    """
        Pytorch model for the DQN algorithm.
    """
    def __init__(self, h, w, outputs):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(config.CAPTURE_N_FRAMES, 16, kernel_size=5, stride=2)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=2)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
        self.bn3 = nn.BatchNorm2d(32)
        self.conv4 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
        self.bn4 = nn.BatchNorm2d(32)

        # Number of Linear input connections depends on output of conv2d layers
        # and therefore the input image size, so compute it.
        def conv2d_size_out(size, kernel_size = 5, stride = 2):
            return (size - (kernel_size - 1) - 1) // stride  + 1
        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(conv2d_size_out(w))))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(conv2d_size_out(h))))
        linear_input_size = convw * convh * 32
        self.head = nn.Linear(linear_input_size, outputs)

    # Called with either one element to determine next action, or a batch
    # during optimization. Returns tensor([[left0exp,right0exp]...]).
    def forward(self, x):
        x = Func.relu(self.bn1(self.conv1(x)))
        x = Func.relu(self.bn2(self.conv2(x)))
        x = Func.relu(self.bn3(self.conv3(x)))
        x = Func.relu(self.bn4(self.conv4(x)))
        x = self.head(x.view(x.size(0), -1))
        return x