# <img src="./medias/TMForge_Banner.png" width="1000" height="200" />
*The tool is still in Beta and have a lot of bugs. To make a stable release come faster, feel free to help by contributing*<br>

## An opensource set of tool for reinforcement learning on Trackmania 2020.
The main features provided by TMForge are:
1. An OpenAI's Gym-like api for a Trackmania environment
2. An experiments-oriented approach of the RL algorithm.
3. A complete set of tools to help you implement your algorithms.

### Why an experiments-oriented approach ?
The experiment oriented approach allow you to easily save the metrics of your algorithms. It helps you with hyperparameters tuning and to compare algortihms.

## Requirements
- Windows
- [Openplanet](https://openplanet.nl/)
- Club access on [Trackmania 2020](https://www.ubisoft.com/fr-fr/game/trackmania/trackmania)
- [pywin32](https://pypi.org/project/pywin32/)
- [OpenCV-Python](https://pypi.org/project/opencv-python/) and [numpy](https://numpy.org/)
- (Demos only) [Pytorch](https://pytorch.org/get-started/locally/)

## Installation
Once all the requirements are satisfied, you can clone the repository. The only thing to do is move the scipt `openplanetScript/Plugin_TMForge.as` into your openplanet script folder (usually `C:/Users/[Username]/Openplanet4/Scripts/`).
From there you can open the game and go to the map you wan to train your agent on and run one of the followinf modes:
- To test if the binding is correctly working, run the command `python tmforge.py test_binding`
- To train an algorithm, run the command `python tmforge.py run_algorithm {algorithm folder}`
- To evaluate an experiment, run the command`python tmforge.py test_experiment {experiment folder}`

## Developing your own algortihm:
To make your own implementation of reinforcement learning on trackmania you can use two levels of abstraction.
1. The gym-like trackmania environment API.
2. The experiment oriented APi
To learn more about the possibilities please have a look at the DQN implementation that you will find in the "algorithms" folder

## DQN Implementation
The DQN implementation's goal is to demonstrate how to use the tool. No hyperparameter set has been found to perform well on the game yet for this algorithm. 

### Technical Performances
The DQN implementation has been tested only on one poor hardware configuration. To give n idea of the performances, here are the metrics for the default configuration:

| CPU               | GPU               | Training Steps/s | Training steps     | Time               | Episodes           |
| ----------------- | ----------------- | ---------------- | ------------------ | ------------------ | ------------------ |
| AMD FX-4300       | NVIDIA GTX 750 TI | 3.942            | 57816              | 4h 4min 27sec      | 300                |

Feel free to complete this table with your experiments

