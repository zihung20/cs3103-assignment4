# Update the plot so that the x-axis uses the 'time stamps' column instead of sample index.
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

sender = pd.read_csv("./statistics/sender_stats.csv")
receiver = pd.read_csv("./statistics/receiver_stats.csv")
# Use receiver's 'time stamps' column as the shared x-axis
time_stamps = receiver["time stamps"].values

# If sender has fewer RTT samples, spread them evenly across the same time range
if "RTT (ms)" in sender.columns:
    rtt_values = sender["RTT (ms)"].values
    rtt_x = np.linspace(time_stamps.min(), time_stamps.max(), len(rtt_values))
else:
    rtt_values = None

plt.figure(figsize=(10, 6))

# Plot receiver metrics
for col in receiver.select_dtypes(include="number").columns:
    if col != "time stamps":
        plt.plot(time_stamps, receiver[col], label=f"Receiver - {col}", linestyle='--', marker='x')

# Plot sender RTT evenly across timestamps
if rtt_values is not None:
    plt.plot(rtt_x, rtt_values, label="Sender - RTT (ms)", color='tab:orange', marker='o')

plt.title("Sender RTT and Receiver Metrics Over Time")
plt.xlabel("Time Stamps (ms)")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("./statistics/ender_receiver_evenly_spread.png")
plt.show()
