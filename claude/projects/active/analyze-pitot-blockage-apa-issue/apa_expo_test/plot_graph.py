#!/usr/bin/env python3
import csv
import matplotlib.pyplot as plt

# Read the CSV file
x_values = []
y1_values = []
y2_values = []

with open('original_vs_smooth.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        x_values.append(float(row[0]))
        y1_values.append(float(row[1]))
        y2_values.append(float(row[2]))

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(x_values, y1_values, label='Original', marker='o', markersize=3)
plt.plot(x_values, y2_values, label='Smooth', marker='s', markersize=3)

plt.xlabel('Airspeed (cm/s)')
plt.ylabel('TPA Factor')
plt.title('Original vs Smooth TPA Factor')
plt.legend()
plt.grid(True, alpha=0.3)

# Save the plot
plt.savefig('tpa_comparison.png', dpi=150, bbox_inches='tight')
print("Graph saved as 'tpa_comparison.png'")

# Optionally display the plot
plt.show()
