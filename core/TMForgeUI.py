"""

    UI wrapper you can use to display your metrics during training.
    The ui will not appear on the game capture.

"""

import cv2
import time

windowName = "Trackmania Forge"

class TMForgeUI:
    """
        UI wrapper you can use to display your metrics during training.
        The ui will not appear on the game capture.
    """
    def __init__(self):
        pass

    def draw(self, screen):
        """
            params:
                screen: np.array representing the image of the ui
        """
        cv2.imshow(windowName, screen)
        # Move the window under the openplanet control bar
        cv2.moveWindow(
            windowName,
            10, 40
        )
        # Brinf the ui window to front to be over the trackmania window
        cv2.setWindowProperty(windowName, cv2.WND_PROP_TOPMOST, 1)
        # Detect a push on the 'q' button to quit
        if (cv2.waitKey(25) & 0xFF == ord('q')):
            cv2.destroyAllWindows()
            return False
        return True