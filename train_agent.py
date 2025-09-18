import numpy as np, time
from focus_detector import start_detector, stop_detector, get_latest_state, detector_running
from focus_env import FocusEnv

# Start the detector thread (opens camera window)
start_detector()
time.sleep(1.0)  # allow camera warm-up

env = FocusEnv(get_latest_state, step_duration=0.2)

alpha, gamma, epsilon = 0.1, 0.9, 0.2
episodes, steps_per_episode = 20, 50

Q = np.zeros((env.observation_space.n, env.action_space.n))

try:
    for ep in range(episodes):
        if not detector_running():
            print("\nDetector stopped — ending training.")
            break

        state, _ = env.reset()
        for t in range(steps_per_episode):
            if not detector_running():
                print("\nDetector stopped during episode.")
                break

            # epsilon-greedy action
            action = env.action_space.sample() if np.random.rand() < epsilon else int(np.argmax(Q[state]))
            next_state, reward, terminated, truncated, _ = env.step(action)

            Q[state, action] += alpha * (reward + gamma * np.max(Q[next_state]) - Q[state, action])
            state = next_state

        print(f"Episode {ep+1}/{episodes} finished. Current Q-table:\n{Q}\n")

except KeyboardInterrupt:
    print("\nTraining interrupted by user.")

finally:
    stop_detector()
    print("\nDetector stopped. Final Q-table:\n", Q)
