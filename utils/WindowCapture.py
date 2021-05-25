import numpy as np
import cv2
import win32gui, win32ui, win32con
import time

from ctypes import windll


user32 = windll.user32
user32.SetProcessDPIAware() # optional, makes functions return real pixel numbers instead of scaled values

full_screen_rect = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

def is_full_screen():
    try:
        hWnd = user32.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hWnd)
        return rect == full_screen_rect
    except:
        return False

class WindowCapture:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    c = 0

    # constructor
    def __init__(self, window_name):
        # find the handle for the window we want to capture
        self.window_name = window_name
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

        self.started_in = False
        active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if active_window == self.window_name:
            self.started_in = True

        self.update_dimensions()

    def update_dimensions(self):
        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        isFullScreen =  win32gui.GetWindowRect(self.hwnd) == full_screen_rect
        self.isFullScreen = isFullScreen
        self.isTrueFullscreen = is_full_screen()
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        if not isFullScreen:
            # account for the window border and titlebar and cut them off
            border_pixels = 8
            titlebar_pixels = 30
            self.w = self.w - (border_pixels * 2)
            self.h = self.h - titlebar_pixels - border_pixels
            self.cropped_x = border_pixels
            self.cropped_y = titlebar_pixels

            # images into actual screen positions
            self.offset_x = window_rect[0] + self.cropped_x
            self.offset_y = window_rect[1] + self.cropped_y

        else:
            self.offset_x, self.offset_y = 0, 0
            self.cropped_x, self.cropped_y = 0, 0
                

    def get_screenshot(self):
        self.update_dimensions()
        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        try:
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
            cDC.SelectObject(dataBitMap)
            cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)
            t_frame = time.time()
            # convert the raw data into a format opencv can read
            #dataBitMap.SaveBitmapFile(cDC, 'debug{}.bmp'.format(self.c))
            self.c+=1
            signedIntsArray = dataBitMap.GetBitmapBits(True)
            img = np.fromstring(signedIntsArray, dtype='uint8')
            img.shape = (self.h, self.w, 4)

            # free resources
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())

            # drop the alpha channel, or cv.matchTemplate() will throw an error like:
            #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
            #   && _img.dims() <= 2 in function 'cv::matchTemplate'
            img = img[...,:3]

            # make image C_CONTIGUOUS to avoid errors that look like:
            #   File ... in draw_rectangles
            #   TypeError: an integer is required (got type tuple)
            # see the discussion here:
            # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
            img = np.ascontiguousarray(img)
            return img, t_frame
        except win32ui.error:
            pass

    def get_window_rect(self):
        x, y, x2, y2 = win32gui.GetWindowRect(self.hwnd)
        return x, y, x2 - x, y2 - y