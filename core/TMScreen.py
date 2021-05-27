"""

    Handler for the screen capture

"""

from collections import deque
import threading
import numpy as np
import cv2
import config

from utils.WindowCapture import WindowCapture

class TMScreen:
    """
        Handler for the screen capture
    """
    def __init__(self, max_buffer_size=60):
        """
            params:
                max_buffer_size: Number of frames to keep track of
        """
        self.max_buffer_size = max_buffer_size
        # Capture class
        self.tm_capture = WindowCapture("Trackmania")
        # Buffer
        self.tm_frame_buffer = deque(maxlen=max_buffer_size)
        # Keep track of the timestamp of the frames for sync
        self.tm_frame_time_buffer = deque(maxlen=max_buffer_size)

        self.is_capturing = False
        self._capture_thread = None

    def capture(self):     
        """
            Create the screen capture thread
        """       
        if self.is_capturing:
            return False

        self.is_capturing = True
        # Start the thread
        self._capture_thread = threading.Thread(target=self._capture)
        self._capture_thread.start()

        return True

    def _capture(self):
        """
            Take continuously screenshots of the game
        """
        while self.is_capturing:
            # Take screenshot
            screen, time = self.tm_capture.get_screenshot()
            # Resize it
            screen = cv2.resize(screen, (config.CAPTURE_IMG_WIDTH, config.CAPTURE_IMG_HEIGHT))
            if config.CAPTURE_GREYSCALE:
                screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            # stores it in the buffer
            self.tm_frame_buffer.append(screen)
            self.tm_frame_time_buffer.append(time)

    def stop(self):
        """
            Stop / Join the screen capture thread
        """
        if not self.is_capturing:
            return False

        self.is_capturing = False

        if self._capture_thread is not None:
            self._capture_thread.join(timeout=1)
            self._capture_thread = None

        return True

    def getFrames(self, n_frames=1):
        """
            Return the last "n_frames" frames of the buffer and their associated timestamp 
        """
        n = len(self.tm_frame_buffer)
        if n_frames <= n:
            frames = [self.tm_frame_buffer[i] for i in range(n - n_frames, n)]
            frames = np.stack(frames, axis=0)
            times = [self.tm_frame_time_buffer[i] for i in range(n - n_frames, n)]
            return frames, times
        return None