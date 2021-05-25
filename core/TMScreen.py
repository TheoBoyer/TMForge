from collections import deque
import threading
import numpy as np
import cv2
import config

from utils.WindowCapture import WindowCapture

class TMScreen:
    def __init__(self, max_buffer_size=60):
        self.max_buffer_size = max_buffer_size
        self.tm_capture = WindowCapture("Trackmania")
        self.tm_frame_buffer = deque(maxlen=max_buffer_size)
        self.tm_frame_time_buffer = deque(maxlen=max_buffer_size)
        self.is_capturing = False
        self._capture_thread = None

    def capture(self):        
        if self.is_capturing:
            return False

        self.is_capturing = True

        self._capture_thread = threading.Thread(target=self._capture)
        self._capture_thread.start()

        return True

    def _capture(self):
        while self.is_capturing:
            screen, time = self.tm_capture.get_screenshot()

            screen = cv2.resize(screen, (config.CAPTURE_IMG_WIDTH, config.CAPTURE_IMG_HEIGHT))

            self.tm_frame_buffer.append(screen)
            self.tm_frame_time_buffer.append(time)

    def stop(self):
        if not self.is_capturing:
            return False

        self.is_capturing = False

        if self._capture_thread is not None:
            self._capture_thread.join(timeout=1)
            self._capture_thread = None

        return True

    def getFrames(self, n_frames=1):
        n = len(self.tm_frame_buffer)
        if n_frames <= n:
            frames = [self.tm_frame_buffer[i] for i in range(n - n_frames, n)]
            frames = np.stack(frames, axis=0)
            times = [self.tm_frame_time_buffer[i] for i in range(n - n_frames, n)]
            return frames, times
        return None