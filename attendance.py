import json

with open("attendance.json", "r") as file:
    data = json.load(file)
# print(json.dumps(data, indent=4))

import matplotlib.pyplot as plt
import numpy as np
subjects = [subject["subject_name"] for subject in data["subjects"]]
attendance = [subject["attendance_percentage"] for subject in data["subjects"]]
colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(subjects)))
plt.figure(figsize=(13, 6), facecolor="black")
bars = plt.bar(subjects, attendance, color=colors, edgecolor='gray', linewidth=0.8)
for bar in bars:
    bar.set_alpha(0.9)
plt.title("Attendance Percentage by Subject", fontsize=16, fontweight='bold', pad=20, color="yellow")
plt.xlabel("Subjects", fontsize=24, labelpad=10, color="white")
plt.ylabel("Attendance (%)", fontsize=24, labelpad=10, color="white")
plt.xticks(rotation=40, ha='right', fontsize=10, color="cyan")
plt.yticks(fontsize=10, color="cyan")
plt.grid(axis='y', linestyle='--', alpha=0.4)
for bar, value in zip(bars, attendance):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{value:.1f}%",
        ha='center',
        fontsize=10,
        color='white',
        fontweight='bold'
    )
plt.gca().set_facecolor("#221")
plt.tight_layout()
plt.show()
