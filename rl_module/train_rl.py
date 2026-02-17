# rl_module/train_rl.py
from learning_env import LearningEnvironment
from policy_agent import PolicyAgent
import numpy as np
import matplotlib.pyplot as plt
import os

def train(episodes=200):
    env = LearningEnvironment()
    agent = PolicyAgent(lr=0.05)
    reward_history = []

    for ep in range(episodes):
        state = env.reset()
        total_reward = 0
        # single-episode loop
        while not env.done:
            action = agent.choose_action()
            next_state, reward, done = env.step(action)
            agent.update_policy(reward, action)
            total_reward += reward

        reward_history.append(total_reward)
        if (ep+1) % 10 == 0:
            print(f"Episode {ep+1}: total_reward={total_reward}")

    # Save results & policy
    os.makedirs("rl_module/artifacts", exist_ok=True)
    np.save("rl_module/artifacts/reward_history.npy", reward_history)
    agent.save("rl_module/artifacts/policy.npy")
    # Plot
    plt.plot(reward_history)
    plt.xlabel("Episode")
    plt.ylabel("Total reward")
    plt.title("Reward curve")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    train(episodes=200)
