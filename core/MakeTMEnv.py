import time
import cv2
import config

from core.OpenPlanetBridge import OpenPlanetBridge
from core.TMScreen import TMScreen
from devices.TMKeyboard import TMKeyboard
from core.TMEnv import TMEnv

class MakeTMEnv:
    def __init__(self, controller=TMKeyboard(), blocking_mode=True, manual_override=True):
        self.open_planet_bridge = OpenPlanetBridge()
        self.tm_screen = TMScreen()
        self.controller = controller
        self.blocking_mode = blocking_mode
        self.manual_override = manual_override
        self.bound = False
        self.emergency_stop = False

    def isObservable(self):
        return self.tm_screen.getFrames() is not None and self.open_planet_bridge.getState() is not None

    def bind(self):
        if self.bound:
            return False
        self.open_planet_bridge.capture()
        self.tm_screen.capture()

        if self.blocking_mode:
            print("Waiting for you to run trackmania and load/reload the TMForge script on Openplanet")
            while not self.emergency_stop and not self.isObservable():
                time.sleep(0.1)
        self.bound = True

        return True

    def unbind(self):
        if not self.bound:
            return False
        self.open_planet_bridge.stop()
        self.tm_screen.stop()
        self.bound = False
        return True

    def emergencyStop(self):
        self.emergency_stop = True
    
    def __enter__(self):
        self.bind()
        return TMEnv(
            self.open_planet_bridge,
            self.tm_screen,
            self.controller,
            self.blocking_mode,
            self.manual_override
        )

    def __exit__(self,  exc_type, exc_value, tb):
        self.unbind()
        cv2.destroyAllWindows()

