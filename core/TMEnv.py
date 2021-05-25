"""
    
    TMEnv internal class. If you want to instanciate this, please use the MakeTMEnv() api

    Example of use:
         with MakeTMEnv() as tmenv:
                ...

"""

import time
import config

class TMEnv:
    """
        TMEnv internal class. If you want to instanciate this, please use the MakeTMEnv() api

        Example of use:
            with MakeTMEnv() as tmenv:
                    ...
    """
    def __init__(self,
            open_planet_bridge,
            tm_screen,
            controller,
            blocking_mode,
            manual_override
        ):
        """
            params:
                open_planet_bridge (OpenPlanetBridge): Connection handler with the openplanet script
                tm_screen (TMScreen): Screen capture handler
                controller (TMDevice): Trackmania controller e.g keyboard / controller / joystick
                blocking_mode (boolean): Wether the "reset" method of tmenv will block your code. Strongly advise you to let this to True
                manual_override (boolean): Wether the user should be able to override the agent's actions when using a physicall device.
        """
        # Handlers
        self.open_planet_bridge = open_planet_bridge
        self.tm_screen = tm_screen
        # Other params
        self.controller = controller
        self.blocking_mode = blocking_mode
        self.manual_override = manual_override
        # Internal variables
        self.nCp = 0
        self.last_cp_time = None
        self.done = False
        self.state_acquisition_time = None
        self.fps_buffer = []
        self.wait_hook = None

    def attachToWaitHook(self, func):
        """
            Attach "func" to the waiting hook. func will be called during the waiting phase of the environment's step
        """
        self.wait_hook = func

    def FPSUpdate(self):
        """
            Notify that a new frame has been produced
        """
        self.fps_buffer.append(time.time())
        # Removes all frames older than 1 sec
        t = time.time()
        while t - self.fps_buffer[0] > 1:
            self.fps_buffer.pop(0)

    def getFPS(self):
        """
            Return the number of frames produced in the last second
        """
        return len(self.fps_buffer)

    def getTime(self):
        """
            Return the ingame time of the current run
        """
        # Make sure the game is in run
        self.assertIsInRun()
        return self.open_planet_bridge.getTime()

    def getObservation(self):
        """
            Return the current state. It's a numpy array containing frames. The format is specified in config.py
        """
        # Make sure the game is in run
        self.assertIsInRun()
        resp = self.tm_screen.getFrames(n_frames=config.CAPTURE_N_FRAMES)
        if resp is None:
            raise Exception("Trackmania not detected")
        frames, _ = resp
        return frames

    def calculateReward(self):
        """
            Return the rewards obtained since the last calculateReward call
        """
        # Checkpoint number
        newCp = self.open_planet_bridge.getState()["CP"]
        #print(newCp, self.nCp)
        if newCp > self.nCp:
            # We crossed a new CP
            self.nCp = newCp
            self.last_cp_time = time.time()
            return config.ENV_CP_REWARD
        elif self.open_planet_bridge.isGameStateFinish():
            # We crossed the finish line
            return config.ENV_FINISH_REWARD
        else:
            # Nothing special happened
            return config.ENV_DEFAULT_REWARD

    def reset(self):
        """
            Reset the environment. Note that this reset the run in-game. 
            Warning: this is a blocking function by default.
        """
        # In-game reset of the run
        self.controller.reset()
        self.done = False
        # In-game reset of the run
        if self.blocking_mode:
            while True:
                time.sleep(0.5)
                if self.open_planet_bridge.isInGame():
                    break
                self.controller.reset()
        # Reset the internal state
        self.nCp = 0
        self.last_cp_time = time.time()
        self.FPSUpdate()
        self.state_acquisition_time = time.time()
        # Return the initial state
        return self.getObservation()

    def step(self, action):
        """
            Perform an action and return the new state of the game. This behave accordingly to the config.py file (especially the ENV_MAX_FPS setting)
            This will call the wait hook during waiting phase if you attached a function to it

            params:
                action: The action to perform.

            return:
                tuple:
                    new_state: Observation with the consequences of the action the agent took.
                    reward: Reward obtained sinc the last step
                    done: Boolean saying if the state is terminal. If true the episode is finished. You shouldn't call step anymore unless you call reset()
                    info: Dictionnary with aditionnal informations:
                        performed_action: Action performed during the step (Behave accordingly to the manual_override attribute)
                        is_finished: Boolean saying if the finish line was crossed
                        action_latency: The estimated time passed between the moment at which the frame of the previous state was captured
                                        and the moment  at which the given action was performed in-game
        """
        if self.done:
            return None
        # Make sure the game is in run
        self.assertIsInRun()
        performed_action = action

        # Perform action if it's allowed to
        if self.manual_override:
            action_override = self.controller.getActionOverride()
            if action_override is not None:
                performed_action = action_override
            else:
                self.controller.performAction(action)
        else:
            self.controller.performAction(action)
        action_latency = time.time() - self.state_acquisition_time

        # Call the waiting hook
        if self.wait_hook is not None:
            self.wait_hook()

        # Respect the max FPS limit
        t = time.time()
        dt = t - self.fps_buffer[-1]
        if dt < 1 / config.ENV_MAX_FPS:
            time.sleep(1 / config.ENV_MAX_FPS - dt)

        # Calculate the returned informations
        state = self.getObservation()
        reward = self.calculateReward()
        done = self.open_planet_bridge.isGameStateFinish()
        if config.ENV_PLAYING_TIMEOUT > 0:
            done = done or time.time() - self.last_cp_time > config.ENV_PLAYING_TIMEOUT
            
        self.done = done

        if self.done:
            # Make sure we release all keys
            self.controller.releaseEverything()

        self.FPSUpdate()
        self.state_acquisition_time = time.time()
        return state, reward, done, {
            "performed_action": performed_action,
            "is_finished": self.open_planet_bridge.isGameStateFinish(),
            "action_latency": action_latency
        }

    def assertIsInRun(self):
        """
            throw an error if the game is not in a run
        """
        if not self.open_planet_bridge.isInGameOrFinish():
            raise Exception("You are currently not in run")
