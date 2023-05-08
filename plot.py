import pandas as pd
import numpy as np
import os

folder_path = os.path.join(os.path.dirname(__file__), '..', 'rawdata')
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

for csv_file in csv_files:
    data = pd.read_csv(os.path.join(folder_path, csv_file))
    data['Timestamp'] = pd.to_datetime(data['Timestamp']).dt.tz_localize(None)
    data = data[data['Units'] == 'kW']
    if data.empty:
        print(f"Skipping chart for {csv_file} due to empty data")
        continue
    
    data['Cable'] = data['Feeder ID'].apply(lambda x: 'busbar' if pd.isnull(x) else 'Feeder: ' + str(x)) + ' - ' + data['Description']

    
    pivot_data = data.pivot_table(index='Timestamp', columns='Cable', values='Value', aggfunc='first')
    
    pivot_data_week6 = pivot_data[pd.to_datetime(pivot_data.index).isocalendar().week == 6]
    pivot_data_week50 = pivot_data[pd.to_datetime(pivot_data.index).isocalendar().week == 50]

    if not pivot_data_week6.empty:
        pivot_data = pivot_data_week6
    elif not pivot_data_week50.empty:
        pivot_data = pivot_data_week50
    else:
        print(f"No data available for week 6 and week 50 in {csv_file}")
        continue
    
    output_data = []
    for column in pivot_data.columns:
        original_values = pivot_data[column].dropna()
        future_values = np.minimum((3 * original_values), original_values.max())
        average_future = future_values.mean()
        average_original = original_values.mean()
        worst_case = original_values * (average_future / average_original)
        upper_quartile_original = pivot_data.quantile(0.75, axis=0)[column]

        output_row = {
            'timestamp': original_values.index,
            'Substation': f'{data.iloc[0, 0]} - {data.iloc[0, 1]}',
            'Description': column,
            'original_values': original_values,
            'average_original': average_original,
            'future_values': future_values,
            'average_future': average_future,
            'worst_case': worst_case,
            'upper_quartile_original': upper_quartile_original
        }
        output_data.append(pd.DataFrame(output_row))

    output_df = pd.concat(output_data, ignore_index=True)
    output_df.to_csv(os.path.join(os.path.dirname(__file__), 'processeddata', f'{data.iloc[1, 0]} - {data.iloc[1, 1]}.csv'), index=False)
