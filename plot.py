import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

folder_path = os.path.join(os.path.dirname(__file__), '..', 'data')
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

for csv_file in csv_files:
    data = pd.read_csv(os.path.join(folder_path, csv_file))
    data['Timestamp'] = pd.to_datetime(data['Timestamp']).dt.tz_localize(None)
    data['combined'] = data['Description'] + " - Feeder " + data['Feeder ID'].fillna("Busbar").astype(str)

    try:
        pivot_data = data.pivot(index='Timestamp', columns=['combined', 'Units'], values='Value')
    except ValueError as e:
        print(f"Skipping chart for {csv_file} due to error: {e}")
        continue

    for unit in data['Units'].unique():
        unit_data = pivot_data.loc[:, pivot_data.columns.get_level_values(1) == unit]
        unit_data = unit_data.loc[(unit_data.index >= pd.Timestamp('2023-02-01').tz_localize(unit_data.index.tz)) & (unit_data.index <= pd.Timestamp('2023-02-08').tz_localize(unit_data.index.tz))]
        
        if unit_data.empty:
            print(f"Skipping chart for {csv_file} due to empty unit_data")
            continue

        for column in unit_data.columns:
            if unit == "kW":
                original_values = unit_data[column]

                future_values = np.minimum((3 * original_values), original_values.max())
                average_future = future_values.mean()
                average_original = original_values.mean()

                worst_case = original_values * (average_future / average_original)

                fig, ax = plt.subplots()
                original_values.plot(ax=ax, label='Original kW', linewidth=0.5)
                future_values.plot(ax=ax, label='Total kW - Shift loads', color='green', linewidth=0.5)
                worst_case.plot(ax=ax, label='Total kW - Upgrade transformers', color='#FF7F0E', linewidth=0.25)

                ax.fill_between(original_values.index, future_values, color='green', alpha=0.2)
                ax.fill_between(original_values.index, original_values, color='#1F77B4', alpha=0.4)

                ax.axhline(unit_data.quantile(0.75, axis=0)[column], linestyle='--', color='#1F77B4', linewidth=0.5, label='UpperQuartile Original')
                ax.axhline(average_original, linestyle='--', color='#1F77B4', linewidth=0.5, label='Average Original')
                ax.axhline(average_future, linestyle='--', color='green', linewidth=0.5, label='Average Total')

                ax.set_ylabel('kW')
                ax.set_title(column)
                ax.legend()

                plt.savefig(os.path.join(os.path.dirname(__file__), '..', 'output', f'{data.iloc[1, 0]} - {data.iloc[1, 1]}_{column}.png'), dpi=1000)
                plt.close()

                #try this code, it's shorter but might not work