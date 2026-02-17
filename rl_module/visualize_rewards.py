# rl_module/visualize_rewards.py
import numpy as np
import matplotlib.pyplot as plt

hist = np.load("rl_module/artifacts/reward_history.npy")
plt.plot(hist)
plt.xlabel("Episode")
plt.ylabel("Total reward")
plt.title("Reward history")
plt.grid(True)
plt.show()
