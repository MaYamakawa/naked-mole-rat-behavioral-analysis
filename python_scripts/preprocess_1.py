import numpy as np
import pandas as pd
from typing import Optional, Tuple
import glob
from datetime import datetime, timedelta
from multiprocessing import Pool, get_context
import os

num_cores = os.cpu_count()


def get_location_label(antenna_id_from: str, antenna_id_to: str, is_room_prev, allow_nan=False) -> Tuple[str, bool]:
    # obsolete
    room_dict = {
        "1": "A", "5": "A",
        "2": "B", "3": "B", "7": "B",
        "4": "C", "9": "C",
        "6": "D", "11": "D", "15": "D",
        "8": "E", "12": "E", "17": "E", "13": "E",
        "10": "F", "14": "F", "19": "F",
        "16": "G", "21": "G",
        "18": "H", "22": "H", "23": "H",
        "20": "I", "24": "I"
    }
    corridor_dict = {
        "1": "1", "2": "1", "3": "2", "4": "2",
        "5": "3", "6": "3", "7": "4", "8": "4",
        "9": "5", "10": "5", "11": "6", "12": "6",
        "13": "7", "14": "7", "15": "8", "16": "8",
        "17": "9", "18": "9", "19": "10", "20": "10",
        "21": "11", "22": "11", "23": "12", "24": "12"
    }

    if room_dict.get(antenna_id_from, None) is None:
        return room_dict[antenna_id_to], True

    if room_dict[antenna_id_from] == room_dict[antenna_id_to]:  # same room
        return room_dict[antenna_id_from], True
    elif corridor_dict[antenna_id_from] == corridor_dict[antenna_id_to]:  # same corridor
        return corridor_dict[antenna_id_from], False
    else:  # detection error
        if allow_nan:
            return None, True
        else:
            if is_room_prev:
                return room_dict[antenna_id_to], True
            else:
                # for the next detection error
                return room_dict[antenna_id_from], False


# def hour_minute_second_to_seconds(hour: str, minute: str, second: float) -> float:
#     # convert to seconds. rounds up to 0.1 seconds
#     return round(float(hour) * 3600 + float(minute) * 60 + second, 1)
#     # return round(float(hour - 12) * 3600 + float(minute) * 60 + second, 1)


def hour_minute_second_to_seconds(date: str, hour: str, minute: str, second: float) -> float:
    # convert to seconds. rounds up to 0.1 seconds
    # set noon on the reference date (the first day)
    base_date = datetime.strptime(
        date, "%Y-%m-%d").replace(hour=12, minute=0, second=0, microsecond=0)

    # generate date object from argument
    current_datetime = datetime.strptime(
        f"{date} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S.%f")

    # add 1 day to the reference date if the date has changed
    if current_datetime < base_date:
        current_datetime += timedelta(days=1)

    # calculate the elapsed seconds from the reference date
    elapsed_seconds = (current_datetime - base_date).total_seconds()

    # Round the seconds to the nearest 0.1 second
    return round(elapsed_seconds, 1)


def delete_duplicate_anntena_detection(event_data_df: pd.DataFrame) -> pd.DataFrame:
    # print(event_data_df["Time"])
    # print("shifted")
    # print(event_data_df["Time"].shift(-1))
    return event_data_df[
        (event_data_df["Antenna"] != event_data_df["Antenna"].shift(1)) |
        (event_data_df["Time"] - event_data_df["Time"].shift(1) > 0.3)
    ]


def create_time_table_individual(event_data_individual_df: pd.DataFrame, allow_nan=True) -> pd.Series:
    time_points = np.linspace(0.1, 86400, 864000)
    table_data_sr = pd.Series(index=time_points)

    # estimate location before first detection
    from_time = event_data_individual_df.iloc[0]["Time"]
    from_antenna_id = event_data_individual_df.iloc[0]["Antenna"]
    table_data_sr.loc[:from_time], is_room_prev = get_location_label(
        None, from_antenna_id, True)

    # for i in range(len(event_data_individual_df) - 1):
    #     from_time = event_data_individual_df.iloc[i]["Time"]
    #     to_time = event_data_individual_df.iloc[i + 1]["Time"]
    #     from_antenna_id = event_data_individual_df.iloc[i]["Antenna"]
    #     to_antenna_id = event_data_individual_df.iloc[i + 1]["Antenna"]

    #     table_data_sr.loc[from_time:to_time], is_room_prev = get_location_label(
    #         from_antenna_id, to_antenna_id, is_room_prev, allow_nan=allow_nan)

    # combine the 'Time' and 'Antenna' values of each row into a tuple
    time_antenna_pairs = zip(
        event_data_individual_df["Time"], event_data_individual_df["Antenna"])

    # prepare a variable to store the value from the previous row
    prev_time, prev_antenna = next(time_antenna_pairs)

    for current_time, current_antenna in time_antenna_pairs:
        table_data_sr.loc[prev_time:current_time], is_room_prev = get_location_label(
            prev_antenna, current_antenna, is_room_prev, allow_nan=allow_nan)

        # store the current row's value for the next loop
        prev_time, prev_antenna = current_time, current_antenna

    # estimate location after last detection
    table_data_sr.loc[current_time:], is_room_prev = get_location_label(
        None, current_antenna, is_room_prev)

    return table_data_sr


def process_event_data(event_data: pd.DataFrame, individual_ids: Optional[list] = None, allow_nan=False) -> pd.DataFrame:
    if individual_ids is None:
        individual_ids = event_data["ID"].unique()

    groupby_event_data = event_data.groupby("ID")

    converted_time_table_data_list = []
    for individual_id in individual_ids:
        print(individual_id, "processing")
        event_data_individual_df = groupby_event_data.get_group(individual_id)
        event_data_individual_df = delete_duplicate_anntena_detection(
            event_data_individual_df)

        time_table_data_indeividual_sr = create_time_table_individual(
            event_data_individual_df, allow_nan=allow_nan)
        time_table_data_indeividual_sr.name = individual_id
        converted_time_table_data_list.append(time_table_data_indeividual_sr)

    converted_time_table_data_df = pd.concat(
        converted_time_table_data_list, axis=1)
    converted_time_table_data_df.index.name = "Time"
    return converted_time_table_data_df

def process_individual_data(args):
    individual_id, group, allow_nan = args
    print(individual_id, "processing")
    event_data_individual_df = delete_duplicate_anntena_detection(group)
    print("duplicate deleted")
    time_table_data_individual_sr = create_time_table_individual(
        event_data_individual_df, allow_nan=allow_nan)
    time_table_data_individual_sr.name = individual_id
    return time_table_data_individual_sr

def process_file(args):
    file_path, output_file_folder_name, allow_nan = args
    print("processing" + file_path)
    # event_data_paths = glob.glob(event_file_folder_name + "\\*.csv")
    
    filename = file_path.split("/")[-1]

    event_data_df = pd.read_csv(file_path, dtype={
                                "Antenna": str, "ID": str, "Month": int, "Day": int, "Hour": int, "Minute": int, "Second": float})

    month, date = event_data_df.iloc[0]["Month"], event_data_df.iloc[0]["Day"]
    start_date_str = f"2022-{month}-{date}"
    event_data_df["Time"] = event_data_df.apply(
        lambda row: hour_minute_second_to_seconds(
            start_date_str, row["Hour"], row["Minute"], row["Second"]), axis=1)

    individual_ids = None
    if filename.startswith("b"):
        individual_ids = ["DA", "CY", "CZ", "DB", "DF", "DC", "DJ", "DD", "DI", "DG",
                            "DT", "DP", "DM", "DQ", "DO", "DR", "DS", "DH", "DK", "DN", "DE", "DL"]

    elif filename.startswith("d"):
        individual_ids = ["AH", "BN", "AI", "BF", "BQ", "BL", "BS",
                            "AJ", "BP", "BO", "BI", "BG", "BH", "BR", "BJ", "BK", "BM"]

    elif filename.startswith("hg"):
        individual_ids = ["AX", "BC", "AS", "AL", "AG", "AU", "BB", "AZ",
                             "BA", "AP", "AO", "AY", "AR", "AQ", "AT", "AN", "AV", "AM", "AW"]
    
    elif filename.startswith("ht"):
        individual_ids = ["FO", "FP", "FX", "GF", "GC", "FT", "FQ", "FY", "FS", "GB", "FZ",
                            "FR", "FU", "GE", "GA", "FV", "FW", "GH", "GD", "GJ", "GI", "GG"]

    elif filename.startswith("l"):
        individual_ids = ["ER", "EQ", "ES", "ET", "EX", "FC", "FF", "EZ", "EP", "FD", "EW",
                            "FH", "EU", "FI", "EY", "FG", "FA", "FB", "FK", "FE", "FJ", "EV"]

    result_data = process_event_data(
        event_data_df, individual_ids, allow_nan=allow_nan)
    result_data.index = np.round(result_data.index.values, 1)
    result_data.index.name = "Time"
    result_data.to_csv(output_file_folder_name +
                        "/" + file_path.split("/")[-1])


def process_files(event_file_folder_name, output_file_folder_name, allow_nan=False):
    event_data_paths = glob.glob(event_file_folder_name + "/*.csv")
    args = [(file_path, output_file_folder_name, allow_nan)
            for file_path in event_data_paths]

    with get_context("fork").Pool(processes=num_cores - 3) as pool:
        pool.map(process_file, args)


def process_execution_event_to_table():
    event_file_folder_name = "data/event_data"
    output_file_folder_name = "data/processed_data/table_data_with_nan"
    process_files(event_file_folder_name,
                  output_file_folder_name, allow_nan=True)

    output_file_folder_name = "data/processed_data/table_data"
    process_files(event_file_folder_name,
                  output_file_folder_name, allow_nan=False)


if __name__ == "__main__":

    event_file_folder_name = "data/event_data"
    output_file_folder_name = "data/processed_data/table_data_with_nan"
    process_files(event_file_folder_name,
                  output_file_folder_name, allow_nan=True)

    output_file_folder_name = "data/processed_data/table_data"
    process_files(event_file_folder_name,
                  output_file_folder_name, allow_nan=False)
