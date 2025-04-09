import os
import pandas as pd
import numpy as np
from multiprocessing import Pool, freeze_support, get_context
import time

num_cores = os.cpu_count()


def find_nest(df):
    data = df.drop(columns=["Time"]).astype(str).to_numpy()
    df['Time'] = df['Time'].astype(float)

    # count the number of occurrences of each location at each time point
    unique_labels, counts = np.unique(data, return_counts=True)
    count_matrix = np.zeros((data.shape[0], len(unique_labels)), dtype=int)

    for i, label in enumerate(unique_labels):
        count_matrix[:, i] = np.sum(data == label, axis=1)

    # calculate the moving average (window of 6 hours of 0.1 sec records)
    window_size = 6 * 60 * 60 * 10
    rolling_count = np.apply_along_axis(
        lambda m: np.convolve(m, np.ones(window_size) /
                              window_size, mode='same'),
        axis=0, arr=count_matrix)

    # obtain the index of the location with the maximum number of individuals
    nest_indices = np.argmax(rolling_count, axis=1)

    # map from index to location
    nest_location = [unique_labels[i] for i in nest_indices]

    result_df = pd.DataFrame(
        {'Time': df['Time'].round(1), 'Nest': nest_location})

    return result_df


def process_single_file(file_name, input_folder, output_folder, monitor=True):
    if monitor:
        print(f'Processing {file_name}')

    file_path = os.path.join(input_folder, file_name)
    df = pd.read_csv(file_path, dtype=str)

    nest_df = find_nest(df)
    output_file_path = os.path.join(output_folder, f'nest_{file_name}')
    nest_df.to_csv(output_file_path, index=False)


def process_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    csv_files = [file for file in os.listdir(
        input_folder) if file.endswith('.csv')]

    start_time = time.time()
    with get_context("fork").Pool(6) as pool:
        pool.starmap(process_single_file, [
                     (file, input_folder, output_folder) for file in csv_files])
    end_time = time.time()
    print(f'processing time：{end_time - start_time}')


if __name__ == '__main__':
    # from preprocess_event_data_to_table import process_execution_event_to_table
    # process_execution_event_to_table()

    # add freeze_support for multiprocessing on windows
    freeze_support()

    process_files('data/processed_data/table_data_with_nan',
                   'data/processed_data/nest_def_with_nan')
    # process_files('processed_data\\table_data', 'processed_data\\nest_def')

    # process_csv_files_parallel()
