"""

    Base class for virtual devices. To see an example of implementation go check in the "devices" folder

"""

class TMDevice:
    """
        Base class for virtual devices. To see an example of implementation go check in the "devices" folder
    """
    def __init__(self):
        pass

    def performAction(self, action):
        """
            Perform the given action in game
        """
        raise Exception("performAction not implemented by your device")

    def reset(self):
        """
            Reset the run in-game
        """
        raise Exception("reset not implemented by your device")

    def getActionOverride(self):
        """
            Check if a physicall device is trying to override the actions and return the actions performed by the physicall device
        """
        raise Exception("checkActionOverride not implemented by your device")

    def actionToString(self, action):
        """
            Return the string representation of the action
        """
        raise Exception("actionToString not implemented by your device")

    def releaseEverything(self):
        """
            Release all keys / buttons
        """
        raise Exception("releaseEverything not implemented by your device")