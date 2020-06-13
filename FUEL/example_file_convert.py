import pandas as pd
import numpy as np


def stove_info(dataframe):
    """Creating stove dataframe.

    Args:
        dataframe : The un-altered .csv file

    Returns:
        df_stoves : A dataframe containing all study sensor readings and timestamps
        stoves : A list of all stoves found in study data
        fuels : A list of all fuels found in study data

    """
    stove_info_start = []
    household_id = "no household id"
    for (r, name) in enumerate(dataframe[0]):
        if name == "household id:":
            household_id = dataframe[1][r]
        if name == "timestamp":
            stove_info_start = r
            break

    if type(stove_info_start) is list:
        raise ImportError("Could not find the beginning of data. Please ensure that there are appropriate "
                                "column headers and that the timestamp column is labeled as timestamp.")

    df_stoves = dataframe.iloc[stove_info_start:, :]
    df_stoves = df_stoves.fillna(method='ffill')  # fill any missing values at end of dataframe with previous value
    df_stoves, stoves, fuels = format_columns(df_stoves)
    df_stoves = df_stoves[1:]
    df_stoves = df_stoves.reset_index(drop=True) # must reset the index so that cooking events can be plotted
    df_stoves = reformat_dataframe(df_stoves)

    return df_stoves, stoves, fuels, household_id


def format_columns(dataframe):
    '''Renames columns appropriately.

    Args:
        dataframe : The dataframe containing all study sensor readings and timestamps (df_stoves)

    Returns:
        dataframe : The df_stoves dataframe with appropriate column headers
        stoves : A list of all stoves found in study data
        fuels : A list of all fuels found in study data

    '''

    dataframe.columns = dataframe.iloc[0]
    dataframe.columns = map(str.lower, dataframe.columns)

    stoves = []
    fuels = []

    for col in dataframe:
        if 'usage' in col:
            del dataframe[col]
        if 'temperature' in col:
            stove_name = col.split(' ')[0]
            if stove_name == '3pierres' or stove_name == '3':
                stove_name = '3stone'
            stoves.append(stove_name)
            dataframe = dataframe.rename(columns={col: stove_name})
        if 'fuel' in col:
            fuel_type = col.split(' ')[0]
            fuels.append(fuel_type)
            dataframe = dataframe.rename(columns={col: fuel_type})

    return dataframe, stoves, fuels


def reformat_dataframe(dataframe):
    ''''Reformats the dataframes timestamps and sensor data.

    Args:
        dataframe : The dataframe containing all study sensor readings and timestamps (df_stoves)

    Returns:
        dataframe : The df_stoves dataframe with the timestamp column converted to datetime and all sensor values
                    converted to floats
    '''
    dataframe = dataframe.apply(lambda x: np.float64(x) if x.name != 'timestamp' else x)

    dataframe['timestamp'] = dataframe['timestamp'].astype('datetime64[ns]')

    return dataframe


def reformat_example_files(datafile_path):
    """Reformatting the datafiles so that they can be ran in household.py.

    Args:
        str : The datafile path

    Returns:
        df_stoves : A dataframe (df_stoves) containing only necessary information that is appropriate formatted
        stoves : A list of all stoves in study data
        fuels : A list of all fuels in study data

    """

    if type(datafile_path) != str:
        raise ValueError("Must put in file name as a String!")

    data = pd.read_csv(datafile_path, header=None)

    # converting the entire dataframe to lower case to make it more universal
    data = data.applymap(lambda s:s.lower() if type(s) == str else s)

    df_stoves, stoves, fuels, household_id = stove_info(data)

    return df_stoves, stoves, fuels, household_id

