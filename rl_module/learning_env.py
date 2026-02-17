# rl_module/learning_env.py
import numpy as np

class LearningEnvironment:
    """
    Lightweight simulated learning environment.
    state = student progress score
    actions:
      0 -> easier content
      1 -> moderate content
      2 -> harder content
    """

    def __init__(self, max_state=10):
        self.max_state = max_state
        self.reset()

    def reset(self):
        self.state = 0
        self.done = False
        return self.state

    def step(self, action):
        # stochastic reward model (toy simulation)
        if action == 0:
            reward = np.random.choice([0, 1], p=[0.6, 0.4])
        elif action == 1:
            reward = np.random.choice([0, 2], p=[0.3, 0.7])
        elif action == 2:
            reward = np.random.choice([-1, 3], p=[0.5, 0.5])
        else:
            reward = 0

        self.state += reward
        if self.state >= self.max_state:
            self.done = True

        return self.state, reward, self.done
