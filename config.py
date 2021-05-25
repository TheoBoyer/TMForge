###
# Capture settings
### 
# Dimension of the images captured
CAPTURE_IMG_WIDTH = 128
CAPTURE_IMG_HEIGHT = 77
CAPTURE_N_FRAMES = 3
###
# OpenplanetBridgeSettings
###
# Time of the run threshold before considering that the run started
OP_CHRONO_TO_WAIT_BEFORE_PLAYING = -200
###
# Env settings
###
# FPS goal to reach. IMPORTANT: For training stability you should set this value under the true performances of your hardware to keep the FPS as constant as possible 
ENV_MAX_FPS = 5
# Reward to attribute when a cp is crossed
ENV_CP_REWARD = 1
# Reward to attribute when the finish line is crossed
ENV_FINISH_REWARD = 1
# Reward to attribute when nothing special happens
ENV_DEFAULT_REWARD = -0.01
# Max time allowed for the agent between two CPS before considering it's stuck
ENV_PLAYING_TIMEOUT = 30
###
# Draw settings
###
# Size of the sub-windows of a SplittedLayoutWindow
DRAW_LAYOUT_HEIGHT = 70
DRAW_LAYOUT_WIDTH = 100
# Padding to make space for the name of the variable
DRAW_LAYOUT_TITLE_PADDING = 15
DRAW_LAYOUT_HEIGHT_DRAWER = DRAW_LAYOUT_HEIGHT - DRAW_LAYOUT_TITLE_PADDING
# Padding to make space for the graduation of a plot
DRAW_LAYOUT_GRADUATION_PADDING = 10