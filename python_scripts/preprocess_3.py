"""
Toilet chamber
2B 12/15-25 I, 12/26-12/30 G, 12/31-1/16 I
2D All days C
HG 6/28-7/19 A, 7/20- C
HT 1/18-2/13 19:00 A, 2/13 19:00- C
LOC 12/14-17 G, 12/18- C

Garbage chamber
HT -2/7 F, 2/8-2/13 5:00 I, 2/13 5:00- H
Other colonies All days E
"""

import pandas as pd
from datetime import datetime, timedelta
import glob
from multiprocessing import Pool, get_context

# function to assign values to the 'Toilet' column according to specific conditions
def set_toilet_values(row, start_date, condition):
    # calculate date and time
    timestamp = start_date + timedelta(seconds=row['Time'])
    
    if condition == 'b':
        if start_date.month == 12 and start_date.day < 26 or timestamp.month == 1 and timestamp.day < 16:
            return 'I'
        elif start_date.month == 12 and timestamp.day < 31:
            return 'G'
        else:
            return 'I'
    elif condition == 'd':
        return 'C'
    elif condition == 'hg':
        if timestamp.month == 6 or timestamp.month == 7 and timestamp.day < 20:
            return 'A'
        else:
            return 'C'
    elif condition == 'ht':
        if timestamp.month == 1 or timestamp.month == 2 and timestamp.day < 13 or timestamp.month == 2 and timestamp.day == 13 and timestamp.hour < 19:
            return 'A'
        else:
            return 'C'
    elif condition == 'loc':
        if timestamp.month == 12 and timestamp.day < 18:
            return 'I'
        else:
            return 'C'        
    else:
        return 'C'  # default value when no condition is met

def set_garbage_values(row, start_date, condition):
    # calculate date and time
    timestamp = start_date + timedelta(seconds=row['Time'])
    
    if condition == 'ht':
        if timestamp.month == 1 or timestamp.month == 2 and timestamp.day < 8:
            return 'F'
        elif timestamp.month == 2 and timestamp.day > 7 and timestamp.day < 13 or timestamp.month == 2 and timestamp.day == 13 and timestamp.hour < 5:
            return 'I'
        else:
            return 'H'
    else:
        return 'E'  # default value when no condition is met

# function to get condition and date from filename
def extract_condition_and_date(filename):
    parts = filename.split('_')
    condition = parts[1][0:-8]
    date_str = parts[1][-8:-4]
    start_date = datetime.strptime(date_str, '%m%d')
    return condition, start_date

# function to load a CSV, process data, add columns, and save
# def process_file(folder_path, filename):
    # condition, start_date = extract_condition_and_date(filename)
    # print(condition, start_date)
    # df = pd.read_csv(folder_path+"/"+filename)
    # df['Garbage'] = 'E'
    # df['Toilet'] = df.apply(lambda row: set_toilet_values(row, start_date, condition), axis=1)
    # new_filename = f"processed_data/room_def/{filename}"
    # df.to_csv(new_filename, index=False)


# function to load a CSV, process data, add columns, and save
def process_file_nan_filled_by_nest(folder_path, filename):
    # function to get condition and date from filename
    condition, start_date = extract_condition_and_date(filename)
    print(condition, start_date)

    df = pd.read_csv(folder_path +"/" + filename)
    
    df['Toilet'] = df.apply(lambda row: set_toilet_values(row, start_date, condition), axis=1)
    df['Garbage'] = df.apply(lambda row: set_garbage_values(row, start_date, condition), axis=1)
    
    new_filename = f"data/processed_data/room_def_with_nan/{filename}"
    df.to_csv(new_filename, index=False)


if __name__ =="__main__":
    # file_paths = glob.glob("processed_data\\nest_def\\*.csv")
    # for file_path in file_paths:
    #     filename = file_path.split("\\")[-1]
    #     process_file("processed_data\\nest_def", filename)
    
    # file_paths = glob.glob("processed_data\\nest_def_with_nan\\*.csv")
    # for file_path in file_paths:
    #     filename = file_path.split("\\")[-1]
    #     process_file_nan_filled_by_nest("processed_data\\nest_def_with_nan", filename)


    # file_paths_nest_def = glob.glob("processed_data/nest_def/*.csv")
    file_paths_nest_def_with_nan = glob.glob("data/processed_data/nest_def_with_nan/*.csv")

    # multiprocessing.Pool
    with get_context("fork").Pool(6) as pool:
        # process_file function
        # pool.starmap(process_file, [("data\\processed_data\\nest_def", filename.split("\\")[-1]) for filename in file_paths_nest_def])
        
        # process_file_nan_filled_by_nest function
        pool.starmap(process_file_nan_filled_by_nest, [("data/processed_data/nest_def_with_nan", filename.split("/")[-1]) for filename in file_paths_nest_def_with_nan])