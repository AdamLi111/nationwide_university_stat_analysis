# Re-import required libraries since the execution state was reset
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Define new categories and values
categories = ['Academics', 'Resources', 'Value', 'Outcomes', 'Selectiveness']
values = [10, 7, 9, 8, 8]

# Ensure that categories and values have the same length before creating a DataFrame
df = pd.DataFrame({'Categories': categories, 'Values': values})

# Number of variables
num_vars = len(categories)

# Compute angle for each category
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

# Repeat the first value to close the circular graph
values += values[:1]
angles += angles[:1]

# Plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# Draw the radar chart
ax.fill(angles, values, color='green', alpha=0.25)
ax.plot(angles, values, color='green', linewidth=2)

# Add labels
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)

# Set axis limit and grid
ax.set_yticks(range(1, 11))  # Define 10-axis levels
ax.set_ylim(0, 10)  # Set limit to 10

# Calculate the area of the bonded polygon using Shoelace formula
x_coords = [np.cos(angle) * value for angle, value in zip(angles, values)]
y_coords = [np.sin(angle) * value for angle, value in zip(angles, values)]

area = 0.5 * abs(sum(x_coords[i] * y_coords[i+1] - x_coords[i+1] * y_coords[i] for i in range(num_vars)))

# Display the plot
plt.title(f"Radar Chart with Area: {area:.2f}")
plt.show()

# Return the calculated area
area
print(area)