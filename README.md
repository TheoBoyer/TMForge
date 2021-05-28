# <img src="./medias/TMForge_Banner.png" width="1000" height="200" />
*The tool is still in Beta and has a lot of bugs. To make a stable release come faster, feel free to help by contributing*<br>

## An open-source set of tools for reinforcement learning on Trackmania 2020.
The main features provided by TMForge are:
1. An OpenAI's Gym-like API for a Trackmania environment
2. An experiment-oriented approach of the RL algorithm.
3. A complete set of tools to help you implement your algorithms.

### Why an experiment-oriented approach ?
The experiment-oriented approach allows you to easily save the metrics of your algorithms. It helps you with hyperparameters tuning and to compare algorithms.

## Requirements
- Windows
- [Openplanet](https://openplanet.nl/)
- Club access on [Trackmania 2020](https://www.ubisoft.com/fr-fr/game/trackmania/trackmania)
- [pywin32](https://pypi.org/project/pywin32/)
- [OpenCV-Python](https://pypi.org/project/opencv-python/), [Pandas](https://pandas.pydata.org/), and [NumPy](https://numpy.org/)
- (Only for the demo) [Pytorch](https://pytorch.org/get-started/locally/)

## Installation
Once all the requirements are satisfied, you can clone the repository. The only thing to do is move the script `openplanetScript/Plugin_TMForge.as` into your openplanet script folder (usually `C:/Users/[Username]/Openplanet4/Scripts/`).
From there you can open the game and go to the map you want to train your agent on and run one of the following modes:
- To test if the binding is correctly working, run the command `python tmforge.py test_binding`
- To train an algorithm, run the command `python tmforge.py run_algorithm {algorithm folder}`
- To evaluate an experiment, run the command`python tmforge.py test_experiment {experiment folder}`
- To resume an experiment, run the command`python tmforge.py resume_experiment {experiment folder}`
Now you can complete the binding by going in-game and reloading the Openplanet TMForge plugin (`Open planet bar -> Developer -> Load/Reload plugin -> TMForge`)
<p align="center">
  <img src="https://i.imgur.com/KMQhCGF.png" /><br>
</p>

## Developing your own algorithm:
To make your implementation of reinforcement learning on Trackmania you can use two levels of abstraction.
1. The gym-like Trackmania environment API.
2. The experiment-oriented API
For the latter, you should create your algorithm folder in the "algorithms" folder. You will have to create two files:
1. train.py: A file containing a "run" function that can both start and resume the training of your algorithm.
2. play.py: A file containing a play method called to evaluate your agent.
If you want to use additional scripts, you should place them in your algorithm's "package" folder.
To learn more about the possibilities please have a look at the "Tutorial" and the "DQN" implementation that you will find in the "algorithms" folder.

## DQN Implementation
The DQN implementation's goal is to demonstrate how to use the tool. The default hyperparameters are still unstable and need to be improved

### Recommendations
If you want to run this algorithm please take into consideration the following:
- The backup files storing the replay buffer can be quite large (~1Go for 10k "buffer_size")
- Aim for stability over performance especially when you choose the "ENV_MAX_FPS" setting. The training easily collapses on long runs.
- Run Trackmania with minimal graphics to use your GPU for the training.

### Technical Performances
The DQN implementation has been tested only on one poor hardware configuration. To give an idea of the performances, here are the obtained metrics for the default configuration:

| CPU               | GPU               | Training Steps/s | Training steps     | Time               | Episodes           |
| ----------------- | ----------------- | ---------------- | ------------------ | ------------------ | ------------------ |
| AMD FX-4300       | NVIDIA GTX 750 TI | 3.942            | 57816              | 4h 4min 27sec      | 300                |

Feel free to create a pull request to complete this table with your experiments.

### Benchmark
The DQN algorithm is being tested on the TMForge official benchmark map. It's simple enough to be finished by an agent but mix several surfaces and in-game blocks.
<p align="center">
  <img src="https://i.imgur.com/QofS9Mz.png" /><br>
</p>

*The benchmark map is available in the TMForge club*
 For this benchmark, you can find the results of a bunch of runs on [Kaggle](https://www.kaggle.com/wolfy73/trackmania-dqn-results-analysis)
