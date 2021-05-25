import time
import config

from core.OpenPlanetBridge import OpenPlanetBridge
from core.TMScreen import TMScreen

class TMEnv:
    def __init__(self,
            open_planet_bridge,
            tm_screen,
            controller,
            blocking_mode,
            manual_override
        ):
        self.open_planet_bridge = open_planet_bridge
        self.tm_screen = tm_screen
        self.controller = controller
        self.blocking_mode = blocking_mode
        self.manual_override = manual_override
        self.nCp = 0
        self.last_cp_time = None
        self.done = False
        self.fps_buffer = []
        self.wait_hook = None
        self.state_acquisition_time = None

    def attachToWaitHook(self, func):
        self.wait_hook = func

    def FPSUpdate(self):
        self.fps_buffer.append(time.time())
        t = time.time()
        while t - self.fps_buffer[0] > 1:
            self.fps_buffer.pop(0)

    def getFPS(self):
        return len(self.fps_buffer)

    def getTime(self):
        self.assertIsInRun()
        return self.open_planet_bridge.getTime()

    def getObservation(self):
        self.assertIsInRun()
        resp = self.tm_screen.getFrames(n_frames=config.CAPTURE_N_FRAMES)
        if resp is None:
            raise Exception("Trackmania not detected")
        frames, _ = resp
        return frames

    def calculateReward(self):
        newCp = self.open_planet_bridge.getState()["CP"]
        if newCp > self.nCp:
            self.nCp = newCp
            self.last_cp_time = time.time()
            return config.ENV_CP_REWARD
        elif self.open_planet_bridge.isGameStateFinish():
            return config.ENV_FINISH_REWARD
        else:
            return config.ENV_DEFAULT_REWARD

    def reset(self):
        self.controller.reset()
        self.done = False

        if self.blocking_mode:
            while True:
                time.sleep(0.5)
                if self.open_planet_bridge.isInGame():
                    break
                self.controller.reset()
        self.nCp = 0
        self.last_cp_time = time.time()
        self.state_acquisition_time = time.time()
        self.FPSUpdate()
        return self.getObservation()

    def step(self, action):
        if self.done:
            return None
        self.assertIsInRun()
        action_latency = time.time() - self.state_acquisition_time
        performed_action = action
        if self.manual_override:
            action_override = self.controller.getActionOverride()
            if action_override is not None:
                performed_action = action_override
            else:
                self.controller.performAction(action)
        else:
            self.controller.performAction(action)

        if self.wait_hook is not None:
            self.wait_hook()

        t = time.time()
        dt = t - self.fps_buffer[-1]
        if dt < 1 / config.ENV_MAX_FPS:
            time.sleep(1 / config.ENV_MAX_FPS - dt)


        state = self.getObservation()
        reward = self.calculateReward()
        done = self.open_planet_bridge.isGameStateFinish()
        if config.ENV_PLAYING_TIMEOUT > 0:
            done = done or time.time() - self.last_cp_time > config.ENV_PLAYING_TIMEOUT
            
        self.done = done

        if self.done:
            self.controller.releaseEverything()

        self.state_acquisition_time = time.time()
        self.FPSUpdate()
        return state, reward, done, {
            "performed_action": performed_action,
            "is_finished": self.open_planet_bridge.isGameStateFinish(),
            "action_latency": action_latency
        }

    def assertIsInRun(self):
        if not self.open_planet_bridge.isInGameOrFinish():
            raise Exception("You are currently not in run")
