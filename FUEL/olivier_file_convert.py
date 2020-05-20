import pandas as pd
import numpy as np


def reformat_olivier_files(datafile_path):

    if type(datafile_path) != str:
        raise ValueError("Must put in file name as a String!")

    def stove_info(dataframe):
        '''Creating stove data set.'''

        # This function will be called by the init function
        # The file should be formatted such that there is a Timestamp header in the first column of the data set
        # which marks the beginning of the sensor data.
        # This function will create a new data set beginning at the location of that Timestamp header
        # It will then assign the first row as headers and re-format the
        # This function will also call the reformat_dataframe() function to convert the timestamps from strings
        # to datetime

        stove_info_start = []
        for (r, name) in enumerate(dataframe[0]):
            if name == "timestamp":
                stove_info_start = r
                break

        if type(stove_info_start) is list:
            raise ImportError("Could not find the beginning of data. Please ensure that there are appropriate "
                                  "column headers and that the timestamp column is labeled as timestamp.")

        df_stoves = dataframe.iloc[stove_info_start:, :]
        df_stoves, stoves, fuels = format_columns(df_stoves)
        df_stoves = df_stoves[1:]
        df_stoves = df_stoves.reset_index(drop=True) # must reset the index so that cooking events can be plotted
        df_stoves = reformat_dataframe(df_stoves)

        return df_stoves, stoves, fuels

    def format_columns(dataframe):
        '''This function creates the appropriate columns'''

        # first it locates the column headers
        # it then converts all column headers into lower case
        # then removes all columns pertaining to usage (info not needed)
        # pulls out list of stoves and fuels
        # rename all columns with only their stove or fuel type

        dataframe.columns = dataframe.iloc[0]
        dataframe.columns = map(str.lower, dataframe.columns)

        stoves = []
        fuels = []

        for col in dataframe:
            if 'usage' in col:
                del dataframe[col]
            if 'temperature' in col:
                 stove_name = col.split(' ')[0]
                 stoves.append(stove_name)
                 dataframe = dataframe.rename(columns={col: stove_name})
            if 'fuel' in col:
                 fuel_type = col.split(' ')[0]
                 fuels.append(fuel_type)
                 dataframe = dataframe.rename(columns={col: fuel_type})

        return dataframe, stoves, fuels

    def reformat_dataframe(dataframe):
        ''''reformatting the dataframe'''

        # first all values in the dataframe will be converted from a str to a float
        # (with the exception of the timestamp col)
        # then the timestamp will be converted to date time if it is a string

        dataframe = dataframe.apply(lambda x: np.float64(x) if x.name != 'timestamp' else x)

        dataframe['timestamp'] = dataframe['timestamp'].astype('datetime64[ns]')

        return dataframe

    data = pd.read_csv(datafile_path, header=None)
    # I want to convert the entire dataframe to lower case to mak it more universal
    data = data.applymap(lambda s:s.lower() if type(s) == str else s)
    df_stoves, stoves, fuels = stove_info(data)
    return df_stoves, stoves, fuels


if __name__ == "__main__":
    #example
    df, stoves, fuels = reformat_olivier_files('./data_files/HH_38_2018-08-26_15-01-40_processed_v3.csv')
    print(df, stoves, fuels)
