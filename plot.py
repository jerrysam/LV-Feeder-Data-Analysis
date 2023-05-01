import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Replace '721030.csv' with the actual file name and path
csv_file = '721030.csv'

# Read the CSV file into a pandas DataFrame
data = pd.read_csv(csv_file)

# Convert the 'Timestamp' column to a pandas datetime object with timezone
data['Timestamp'] = pd.to_datetime(data['Timestamp']).dt.tz_localize(None)  # Remove the timezone information

# Create a new column with the combined text from the 'Description' and 'Feeder ID' columns
data['combined'] = data['Description'] + " - Feeder " + data['Feeder ID'].astype(str)

# Pivot the DataFrame to create separate columns for each unique value in the 'combined' column
pivot_data = data.pivot(index='Timestamp', columns=['combined', 'Units'], values='Value')

# Get unique values in the 'Units' column
unique_units = data['Units'].unique()

# Get the color palette for the lines
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

# Plot a separate graph for each unique unit
for unit in unique_units:
    unit_data = pivot_data.loc[:, pivot_data.columns.get_level_values(1) == unit]

    # Remove columns that contain missing or invalid values
    unit_data = unit_data.dropna(axis='columns', how='any')
    
    # Convert the "Value" column to numeric data type
    unit_data = unit_data.apply(pd.to_numeric, errors='coerce')
    
    unit_data = unit_data.select_dtypes(include=[np.number])

    if len(unit_data.columns) == 0:
        print(f"No numeric data found for unit {unit}")
        continue

    # Select data for the first week of February
    start_date = pd.Timestamp('2023-02-01').tz_localize(unit_data.index.tz)
    end_date = pd.Timestamp('2023-02-08').tz_localize(unit_data.index.tz)
    unit_data = unit_data.loc[(unit_data.index >= start_date) & (unit_data.index <= end_date)]

    # Calculate the upper quartile for each line
    upper_quartiles = unit_data.quantile(0.75, axis=0)

    # Plot the original values
    fig, ax = plt.subplots()
    unit_data.plot(ax=ax, linewidth=0.25, legend=True)

    # Plot the upper quartile as a flat line across the chart with the same color as the time series
    for i, column in enumerate(upper_quartiles.index):
        upper_quartile = upper_quartiles[column]
        color = colors[i % len(colors)]
        ax.axhline(upper_quartile, color=color, linestyle='--', linewidth=1.5)

    ax.set_ylabel('Value')
    ax.set_title(f'Unit: {unit}')

    # Show the plot
    if unit == "kW":
        plt.show()
