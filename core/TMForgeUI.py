import cv2
import time

windowName = "Trackmania Forge"

class TMForgeUI:
    def __init__(self):
        pass

    def draw(self, screen):
        cv2.imshow(windowName, screen)
        cv2.moveWindow(
            windowName,
            10, 40
        )
        cv2.setWindowProperty(windowName, cv2.WND_PROP_TOPMOST, 1)
        if (cv2.waitKey(25) & 0xFF == ord('q')):
            cv2.destroyAllWindows()
            return False
        return True