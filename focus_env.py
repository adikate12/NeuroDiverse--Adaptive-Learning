import gymnasium as gym
from gymnasium import spaces
import time
from focus_detector import detector_running

class FocusEnv(gym.Env):
    """
    Reads external detector state and gives reward based on action.
    observation_space: 0 = focused, 1 = distracted
    action_space:      0 = give reward, 1 = prompt, 2 = suggest break
    """

    def __init__(self, detector_func, step_duration=0.2):
        super().__init__()
        self.detector_func = detector_func
        self.observation_space = spaces.Discrete(2)
        self.action_space = spaces.Discrete(3)
        self.step_duration = step_duration
        self.state = 1

    def reset(self, *, seed=None, options=None):
        if not detector_running():
            raise RuntimeError("Detector is not running.")
        time.sleep(self.step_duration)
        self.state = self.detector_func()
        return self.state, {}

    def step(self, action):
        if not detector_running():
            # End episode immediately if camera stopped
            return self.state, 0.0, True, False, {}

        time.sleep(self.step_duration)
        self.state = self.detector_func()

        # Simple reward scheme
        if self.state == 0 and action == 0:     # focused & give reward
            reward = 1.0
        elif self.state == 1 and action == 1:   # distracted & prompt
            reward = 1.0
        else:
            reward = -0.2

        return self.state, reward, False, False, {}
