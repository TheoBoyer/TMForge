class TMDevice:
    def __init__(self):
        pass

    def performAction(self, action):
        raise Exception("performAction not implemented by your device")

    def reset(self):
        raise Exception("reset not implemented by your device")

    def getActionOverride(self):
        raise Exception("checkActionOverride not implemented by your device")

    def actionToString(self, action):
        raise Exception("actionToString not implemented by your device")

    def releaseEverything(self):
        raise Exception("releaseEverything not implemented by your device")