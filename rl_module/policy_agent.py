# rl_module/policy_agent.py
import numpy as np

class PolicyAgent:
    """
    Simple policy-based agent with a categorical policy vector.
    """

    def __init__(self, n_actions=3, lr=0.05):
        self.n_actions = n_actions
        self.lr = lr
        # initialize uniform policy
        self.policy = np.ones(self.n_actions) / self.n_actions

    def choose_action(self, state):
        return int(np.random.choice(self.n_actions, p=self.policy))

    def update_policy(self, reward, action):
        # simple policy update (policy gradient-ish, no baseline)
        grad = np.zeros(self.n_actions)
        grad[action] = 1.0
        self.policy += self.lr * reward * grad
        # stability
        self.policy = np.clip(self.policy, 1e-3, 1.0)
        self.policy /= np.sum(self.policy)

    def save(self, path):
        np.save(path, self.policy)

    def load(self, path):
        import numpy as np
        self.policy = np.load(path)
        # ensure normalize
        self.policy = np.clip(self.policy, 1e-3, 1.0)
        self.policy /= np.sum(self.policy)
