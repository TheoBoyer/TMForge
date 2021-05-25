"""

    Set of function usefull to draw an UI

"""


import numpy as np
import config
import cv2

import utils.Keyboard as Keyboard
from core.TMForgeUI import TMForgeUI
from devices.TMKeyboard import TMKeyboard
from math import ceil, floor

# Default font
font = cv2.FONT_HERSHEY_DUPLEX
# Default color
font_color = (0, 155, 227)

def drawBlackBackground(data):
    """
        Draw a black image regardless of the given data
    """
    return np.zeros((config.DRAW_LAYOUT_HEIGHT, config.DRAW_LAYOUT_WIDTH, 3), dtype=np.uint8)

def draw_layout_plot(source, data, color):
    """
        Draw on source the plot of descrete function in data in the given color

        params:
            source (np.array): The image to draw on
            data (list): The source data
            color: The color to plot in
    """
    # Take title padding into account
    pos = (config.DRAW_LAYOUT_GRADUATION_PADDING, config.DRAW_LAYOUT_TITLE_PADDING)
    size = (config.DRAW_LAYOUT_WIDTH - config.DRAW_LAYOUT_GRADUATION_PADDING-5, config.DRAW_LAYOUT_HEIGHT_DRAWER-5)
    # Draw the bondary of the plot
    source = cv2.rectangle(
        source,
        pos,
        (pos[0] + size[0], pos[1] + size[1]),
        color,
        1
    )
    # Not sur about that but meh
    if len(data) > 1:
        vmin, vmax = min(*data), max(*data)
        ymin, ymax = pos[1], pos[1] + size[1]
        dv, dy = vmax - vmin, ymax - ymin
        dv = max(1e-5, dv)
        # Graduation. Plot only entire values. Will improve it using some log-stuff
        grad = list(range(ceil(vmin), floor(vmax) + 1))
        for i in grad:
            yi = int(round(ymin + dy - (i - vmin) * dy / dv))
            # The little line
            source = cv2.line(
                source,
                (pos[0]-2, yi),
                (pos[0], yi),
                (255, 255, 255),
                1
            )
            # The number
            source = cv2.putText(
                source,
                str(i),
                (pos[0]-config.DRAW_LAYOUT_GRADUATION_PADDING, yi), 
                cv2.FONT_HERSHEY_DUPLEX, 
                0.25,
                (255, 255, 255),
                1
            )
                

        iterator = iter(data)
        prev = next(iterator)
        prev_x = pos[0]
        line_thickness = 1
        dx = size[0] / (len(data)-1)
        # Plot the actual data
        for curr in iterator:
            curr_x = prev_x + dx
            source = cv2.line(
                source,
                (int(round(prev_x)), int(round(ymin + dy - (prev - vmin) * dy / dv))),
                (int(round(curr_x)), int(round(ymin + dy - (curr - vmin) * dy / dv))),
                color,
                thickness=line_thickness
            )

            prev_x, prev = curr_x, curr
    return source

def getLastTypeDrawer(params):
    """
        Return a drawer that will display the last value
        params:
            dict containing:
                (optionnal) "pattern": string format to display in (for example {:.4f} to display only 4 digits after the point))
                (optionnal) "lambda": function that handles turn an number into a string (if provided cancel pattern)
    """
    pattern = params.get("pattern", "{}")
    lambda_func = params.get("lambda", lambda x: pattern.format(x))
    def draw(data):
        window = np.zeros((config.DRAW_LAYOUT_HEIGHT, config.DRAW_LAYOUT_WIDTH, 3), dtype=np.uint8)
        text = lambda_func(data[-1])
        size = 0.7
        text_thickness = 1

        textsize = cv2.getTextSize(text, font, size, text_thickness)[0]
        textX = (config.DRAW_LAYOUT_WIDTH - textsize[0]) / 2
        textY = (config.DRAW_LAYOUT_HEIGHT_DRAWER + textsize[1]) / 2
        window = cv2.putText(
            window,
            text,
            (int(round(textX)), int(round(textY)) + config.DRAW_LAYOUT_TITLE_PADDING), 
            font, 
            size,
            font_color,
            text_thickness
        )
        return window
    return draw

def getKeyboardTypeDrawer(params):
    """
        Return a drawer that will display keyboard actions
    """
    def draw(data):
        window = np.zeros((config.DRAW_LAYOUT_HEIGHT, config.DRAW_LAYOUT_WIDTH, 3), dtype=np.uint8)
        action = data[-1]
        action_str = TMKeyboard.ActionToString(action)

        key_draw_size = min(0.7 * config.DRAW_LAYOUT_WIDTH / 3, 0.7 * config.DRAW_LAYOUT_HEIGHT_DRAWER / 2)
        x_left =  config.DRAW_LAYOUT_WIDTH * (1 - key_draw_size * 3 / config.DRAW_LAYOUT_WIDTH) / 2
        x_down = x_up = x_left + key_draw_size
        x_right = x_down + key_draw_size

        y_up = config.DRAW_LAYOUT_HEIGHT_DRAWER * (1 - key_draw_size * 2 / config.DRAW_LAYOUT_HEIGHT_DRAWER) / 2 + config.DRAW_LAYOUT_TITLE_PADDING
        y_left = y_down = y_right = y_up + key_draw_size

        window = cv2.rectangle(
            window,
            (int(round(x_left)), int(round(y_left))),
            (int(round(x_left + key_draw_size)), int(round(y_left + key_draw_size))),
            font_color,
            cv2.FILLED if "←" in action_str else 1
        )

        window = cv2.rectangle(
            window,
            (int(round(x_down)), int(round(y_down))),
            (int(round(x_down + key_draw_size)), int(round(y_down + key_draw_size))),
            font_color,
            cv2.FILLED if "↓" in action_str else 1
        )

        window = cv2.rectangle(
            window,
            (int(round(x_up)), int(round(y_up))),
            (int(round(x_up + key_draw_size)), int(round(y_up + key_draw_size))),
            font_color,
            cv2.FILLED if "↑" in action_str else 1
        )

        window = cv2.rectangle(
            window,
            (int(round(x_right)), int(round(y_right))),
            (int(round(x_right + key_draw_size)), int(round(y_right + key_draw_size))),
            font_color,
            cv2.FILLED if "→" in action_str else 1
        )
        return window
    return draw

def getGraphicLastTypeDrawer(params):
    """
        Return a drawer that will plot values
        params:
            dict containing:
                "maxlen": number of values to plot
                "approx_type: if "last" -> plot the last values
                              if "moving_average" then reduce the data to maxlen using a non padded moving average (1d convolution)
    """
    maxlen = params["maxlen"]
    approx_type = params["approx_type"]
    def draw(data):
        if approx_type == 'last':
            data = data[-maxlen:]
        elif approx_type == 'moving_average':
            if len(data) > maxlen:
                f = len(data) - maxlen + 1
                data = np.convolve(data, np.ones(f) / f, mode='valid')
        else:
            raise ValueError("Unkonw approximation method: " + str(approx_type))
        window = np.zeros((config.DRAW_LAYOUT_HEIGHT, config.DRAW_LAYOUT_WIDTH, 3), dtype=np.uint8)
        window = draw_layout_plot(
            window,
            data,
            font_color
        )
        return window
    return draw

# Bind drawer type to their string names
BINDTYPE2DRAWER = {
    'last': getLastTypeDrawer,
    'keyboard': getKeyboardTypeDrawer,
    'graphic': getGraphicLastTypeDrawer
}

class SplittedLayoutWindow:
    """
        Class that handle an ui from a datasource like Telemetry
    """
    def __init__(self, source, shape):
        """
            params:
                source: data provider (Telemetry)
                shape: shape of sub-windows. tuple like (nb_rows, nb_columns)
        """
        assert len(shape) == 2, "Shape of SplittedLayoutWindow should be of length 2"
        self.source = source
        self.shape = shape
        self.labels = [None for _ in range(shape[0] * shape[1])]
        self.drawers = [drawBlackBackground for _ in range(shape[0] * shape[1])]
        self.ui = TMForgeUI()

    def bind(self, index, variable, type, params={}):
        """
            Bind a metric of the data source to a sub-window
            params:
                index: index of the subwindow to bind
                variable: name of the metric to bind
                type: A name of drawer (last, keyboard, graphic)
                params: Dict containing the parameters of the drawer
        """
        self.labels[index] = variable
        self.drawers[index] = BINDTYPE2DRAWER[type](params)

    def draw(self):
        """
            Draw the UI. Return a boolean saying if the UI request to close the algorithm
        """
        frame = np.zeros((config.DRAW_LAYOUT_HEIGHT * self.shape[0], config.DRAW_LAYOUT_WIDTH * self.shape[1], 3), dtype=np.uint8)
        for i, (label, drawer) in enumerate(zip(self.labels, self.drawers)):
            y, x = config.DRAW_LAYOUT_HEIGHT * (i // self.shape[1]), config.DRAW_LAYOUT_WIDTH * (i % self.shape[1])
            if label is not None:
                data = self.source.get(label)
                if data is not None and len(data):
                    layout = drawer(data)
                    text = label
                    size = 0.3
                    text_thickness = 1
                    # Display the name of the variable
                    textsize = cv2.getTextSize(text, font, size, text_thickness)[0]
                    textX = (config.DRAW_LAYOUT_WIDTH - textsize[0]) / 2
                    textY = (config.DRAW_LAYOUT_TITLE_PADDING + textsize[1]) / 2
                    layout = cv2.putText(
                        layout,
                        text,
                        (int(round(textX)), int(round(textY))), 
                        font, 
                        size,
                        font_color,
                        text_thickness
                    )
                    frame[y:y + config.DRAW_LAYOUT_HEIGHT, x:x + config.DRAW_LAYOUT_WIDTH] = layout
            else:
                data = None
        return self.ui.draw(frame)
