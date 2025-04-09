from multiprocessing import Pool, get_context
import os
import pandas as pd
import numpy as np

# function to process a single file
def process_single_csv_file(csv_file, data_folder='data/processed_data/table_data_with_nan', nest_folder='data/processed_data/nest_def_with_nan'):
    # load each file for RFID detection data
    data_path = os.path.join(data_folder, csv_file)
    nest_path = os.path.join(nest_folder, 'nest_' + csv_file)

    # read csv as df with 'Time' being float64, but the others in str
    data_df = pd.read_csv(data_path, dtype=str)
    nest_df = pd.read_csv(nest_path, dtype=str)
    data_df['Time'] = data_df['Time'].astype(float)
    nest_df['Time'] = nest_df['Time'].astype(float)

    # round the 'Time' column to the nearest 0.1 second
    data_df['Time'] = np.round(data_df['Time'], 1)
    nest_df['Time'] = np.round(nest_df['Time'], 1)

    # merge nest_df with data_df based on the Time column
    merged_df = pd.merge(data_df, nest_df, on='Time', how='left')

    # processing for each column
    for col in data_df.columns:
        if col == 'Time':  # skip Time column
            continue

        # calculate the duration of consecutive NaN values
        nan_start_time = None
        for idx, (time, value, nest) in enumerate(merged_df[['Time', col, 'Nest']].itertuples(index=False)):
            if pd.isna(value):
                if nan_start_time is None:
                    nan_start_time = time
            else:
                if nan_start_time is not None:
                    duration = time - nan_start_time
                    # replace NaN values lasting more than 30 minutes with the nest location
                    if duration >= 1800:
                        merged_df.loc[(merged_df['Time'] >= nan_start_time) & (merged_df['Time'] < time), col] = nest
                        print(f'{csv_file} {col} {nan_start_time} {time} {duration}')
                    nan_start_time = None

    # save the edited DataFrame
    output_path = os.path.join('data/processed_data/table_data_with_nan_filled_by_nest', f'{csv_file}')
    merged_df.drop(columns=['Nest'], inplace=True)  # remove Nest column
    merged_df.to_csv(output_path, index=False)


# function for multiprocessing
def process_csv_files_parallel(data_folder='data/processed_data/table_data_with_nan', nest_folder='data/processed_data/nest_def_with_nan'):
    # get CSV filename in data_folder
    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

    # multiprocessing using Pool
    with get_context("fork").Pool(6) as pool:
        pool.starmap(process_single_csv_file, [(csv_file, data_folder, nest_folder) for csv_file in csv_files])


if __name__ == '__main__':
    process_csv_files_parallel()
