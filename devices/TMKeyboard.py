"""

    Keyboard virtual device. inherit from TMDevice

"""

import time

import utils.Keyboard as Keyboard
from core.TMDevice import TMDevice

# Map actions nuber to keys
TM_KEYBOARD_ACTIONS = [
    [],
    [Keyboard.ARROWRIGHT],
    [Keyboard.ARROWLEFT],
    [Keyboard.ARROWDOWN],
#    [Keyboard.ARROWDOWN, Keyboard.ARROWRIGHT],
#    [Keyboard.ARROWDOWN, Keyboard.ARROWLEFT],
    [Keyboard.ARROWUP],
    [Keyboard.ARROWUP, Keyboard.ARROWRIGHT],
    [Keyboard.ARROWUP, Keyboard.ARROWLEFT],
#    [Keyboard.ARROWUP, Keyboard.ARROWDOWN],
#    [Keyboard.ARROWUP, Keyboard.ARROWDOWN, Keyboard.ARROWRIGHT],
#    [Keyboard.ARROWUP, Keyboard.ARROWDOWN, Keyboard.ARROWLEFT]
]

# Key code to string 
TM_KEYBOARD_ACTIONS_STR = {
    Keyboard.ARROWUP: "↑",
    Keyboard.ARROWDOWN: "↓",
    Keyboard.ARROWLEFT: "←",
    Keyboard.ARROWRIGHT: "→"
}

# Used keycodes
TM_KEYBOARD_USED_KEYS = (Keyboard.ARROWUP, Keyboard.ARROWDOWN, Keyboard.ARROWLEFT, Keyboard.ARROWRIGHT)

class TMKeyboard(TMDevice):
    """
        Keyboard virtual device. inherit from TMDevice
    """
    ACTION_SPACE = len(TM_KEYBOARD_ACTIONS)
    def __init__(self):
        pass

    def performAction(self, action):
        """
            Perform the given action in game
        """
        actions = TM_KEYBOARD_ACTIONS[action]
        for kc in TM_KEYBOARD_USED_KEYS:
            if kc in actions:
                Keyboard.PushKey(kc)
            else:
                Keyboard.ReleaseKey(kc)

    def reset(self):
        """
            Reset the run in-game
        """
        Keyboard.pressKey(Keyboard.ENTER)
        time.sleep(0.2)
        Keyboard.pressKey(Keyboard.SUPPR)

    def getActionOverride(self):
        """
            Check if a physicall device is trying to override the actions and return the actions performed by the physicall device
        """
        physicalKeysPressed = Keyboard.getPhysicalKeysPressed()
        if len(physicalKeysPressed):
            for kc in TM_KEYBOARD_USED_KEYS:
                if kc not in physicalKeysPressed:
                    Keyboard.ReleaseKey(kc)
            return self.physicalKeys2Action(physicalKeysPressed)
        return None

    def actionToString(self, action):
        """
            Return the string representation of the action
        """
        return TMKeyboard.ActionToString(action)

    @staticmethod
    def ActionToString(action):
        """
            Return the string representation of the action. Static method
        """
        action_str = ""

        for a in TM_KEYBOARD_ACTIONS[action]:
            action_str += TM_KEYBOARD_ACTIONS_STR[a]

        return action_str

    def physicalKeys2Action(self, keys):
        """
            Convert the pressed keys into the associated action number
        """
        try:
            action = TM_KEYBOARD_ACTIONS.index(keys)
        except ValueError:
            action = 0
        return action

    def releaseEverything(self):
        """
            Release all keys / buttons
        """
        for kc in TM_KEYBOARD_USED_KEYS:
            Keyboard.ReleaseKey(kc)