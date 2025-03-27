import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def draw_radar_chart(name, values):
    """
    Draws a radar chart for 5 categories based on the provided list of values.

    Parameters:
        values (list): A list of 5 integers representing the values for the categories.

    Returns:
        float: The area of the radar chart polygon.
    """
    if len(values) != 5:
        raise ValueError("The 'values' list must contain exactly 5 elements.")

    # Define the categories
    categories = ['Academics', 'Resources', 'Value', 'Outcomes', 'Selectiveness']

    # Create a DataFrame (possibly useful in the future, leave it here for now)
    df = pd.DataFrame({'Categories': categories, 'Values': values})

    # Number of variables
    num_vars = len(categories)

    # Compute angle for each category
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Repeat the first value to close the circular graph
    values_closed = values + values[:1]
    angles_closed = angles + angles[:1]

    # Plot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Draw the radar chart
    ax.fill(angles_closed, values_closed, color='green', alpha=0.25)
    ax.plot(angles_closed, values_closed, color='green', linewidth=2)

    # Add labels for each category
    ax.set_xticks(angles)
    ax.set_xticklabels(categories)

    # Set axis limits and grid
    ax.set_yticks(range(1, 11))  # Define 10-axis levels
    ax.set_ylim(0, 10)  # Set limit to 10

    # Calculate the area of the polygon using the Shoelace formula
    x_coords = [np.cos(angle) * value for angle, value in zip(angles_closed, values_closed)]
    y_coords = [np.sin(angle) * value for angle, value in zip(angles_closed, values_closed)]

    area = 0.5 * abs(sum(
        x_coords[i] * y_coords[i + 1] - x_coords[i + 1] * y_coords[i]
        for i in range(num_vars)
    ))

    # Display the plot with a title showing the calculated area
    plt.title(f"{name}'s educational quality score: {area:.2f}\n")
    plt.show()

    # Return the calculated area
    return area

def compute_score(values: list):
    # Compute angle for each category
    angles = np.linspace(0, 2 * np.pi, 5, endpoint=False).tolist()

    # Repeat the first value to close the circular graph
    values_closed = values + values[:1]
    angles_closed = angles + angles[:1]

    # Calculate the area of the polygon using the Shoelace formula
    x_coords = [np.cos(angle) * value for angle, value in zip(angles_closed, values_closed)]
    y_coords = [np.sin(angle) * value for angle, value in zip(angles_closed, values_closed)]

    area = 0.5 * abs(sum(
        x_coords[i] * y_coords[i + 1] - x_coords[i + 1] * y_coords[i]
        for i in range(5)
    ))

    return area

# Example usage:
# area = draw_radar_chart("Northeastern University", [7, 9, 0, 4, 0])
#print(area)

print(compute_score([7, 9, 0, 4, 0]))
