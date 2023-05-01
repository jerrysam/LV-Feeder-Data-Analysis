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

    unit_data = unit_data.select_dtypes(include=[np.number])

    # Select data for the first week of February
    start_date = pd.Timestamp('2023-02-01').tz_localize(unit_data.index.tz)
    end_date = pd.Timestamp('2023-02-08').tz_localize(unit_data.index.tz)
    unit_data = unit_data.loc[(unit_data.index >= start_date) & (unit_data.index <= end_date)]

    # Calculate the upper quartile for each line
    upper_quartiles = unit_data.quantile(0.75, axis=0)

    # Find the column with the highest upper quartile value
    max_quartile_column = upper_quartiles.idxmax()

    # Plot the original values only for unit == "kW"
    if unit == "kW":
        original_values = unit_data[max_quartile_column]
        upper_quartile = upper_quartiles[max_quartile_column]

        # Calculate the total values by summing the original and second set of values
        future_values = np.minimum((3*original_values), 0.9*original_values.max())

        # Calculate the average of the total values
        average_future = future_values.mean()
        # Calculate the average of the original values
        average_original = original_values.mean()

        #Calculate the worst case (upgrade transformers) scenario
        growth_multiplier = average_future / average_original
        worst_case = original_values * growth_multiplier

        # Plot the original values, second set of values, and the sum of both
        fig, ax = plt.subplots()
        original_values.plot(ax=ax, label='Original kW', linewidth=1)
        future_values.plot(ax=ax, label='Total kW - Shift loads', color='green', linewidth=0.5)
        worst_case.plot(ax=ax, label='Total kW - Upgrade transformers', color='#FF7F0E', linewidth=0.25)
        # Fill the area under the graph between the second set and total values
        ax.fill_between(original_values.index, future_values, color='gray', alpha=0.2)
        ax.fill_between(original_values.index, original_values, color='gray', alpha=0.4)

        ax.axhline(upper_quartile, linestyle='--', color='#1F77B4', linewidth=0.5, label='UpperQuartile Original')
        ax.axhline(average_original, linestyle='--', color='#1F77B4', linewidth=0.5, label='Average Original')
        ax.axhline(average_future, linestyle='--', color='green', linewidth=0.5, label='Average Total')
        

        ax.set_ylabel('Value')
        ax.set_title(f'Unit: {unit}')
        ax.legend()

        plt.show()
