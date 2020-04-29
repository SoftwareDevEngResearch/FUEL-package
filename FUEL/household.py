import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks


class Household:

    def __init__(self, datafile):
        '''When called this class will load the datafile and separate out the needed information.'''

        # The only input is the file name, which must be a string containing the file path
        # The file will be searched for the column labeled Timestamp and split the information following that into a
        # data set containing all weight and temperature information for the household being observed (this will be
        # The column containing timestamp data will be reformatted from a string into datetime
        # This data set will then be saves as self.df_stoves
        # self.data will contain all of the information in the original file
        # This will create list of stoves and fuels used in the data set

        if type(datafile) != str:
            raise ValueError("Must put in file name as a String!")

        def stove_info(dataframe):
            '''Creating stove data set.'''

            # This function will be called by the init function
            # The file should be formatted such that there is a Timestamp header in the first column of the data set
            # which marks the beginning of the sensor data.
            # This function will create a new data set beginning at the location of that Timestamp header
            # It will then assign the first row as headers and re-format the
            # This function will also call the __reformat_timestamp__() function to convert the timestamps from strings
            # to datetime

            stove_info_start = []
            for (r, name) in enumerate(dataframe[0]):
                if name == "Timestamp":
                    stove_info_start = r
                    break
            if type(stove_info_start) is list:
                raise ImportError("The data set is not formatted correctly.")

            df_stoves = self.data.iloc[stove_info_start:, :]
            df_stoves = df_stoves.reset_index(drop=True)
            df_stoves.columns = df_stoves.iloc[0]
            df_stoves = df_stoves[1:]
            df_stoves = __reformat_timestamp__(df_stoves)
            return df_stoves

        def __reformat_timestamp__(dataframe):
            ''''reformatting the Timestamp from string to datetime'''

            df_stoves = dataframe.apply(lambda x: np.float64(x) if x.name != 'Timestamp' else x)
            df_stoves['Timestamp'] = pd.to_datetime(df_stoves['Timestamp'], format='%m/%d/%Y %H:%M')

            return df_stoves

        def retrieve_stoves(dataframe):
            '''Finding the stove types in the dataframe'''
            stoves = []
            for col in dataframe.columns:
                if "temp" in col.lower():
                    stoves.append(col)
            return stoves

        def retrieve_fuels(dataframe):
            '''Finding fuel types in the dataframe'''

            fuels = []
            for col in dataframe.columns:
                if "fuel" in col.lower():
                    fuels.append(col)
            return fuels

        self.data = pd.read_csv(datafile, header=None)
        self.df_stoves = stove_info(self.data)
        self.stoves = retrieve_stoves(self.df_stoves)
        self.fuels = retrieve_fuels(self.df_stoves)

    def stove_types(self):
        ''' Display stove types captured in data'''

        # This function will produce a list of stoves found in the data set (stove_types) which is easily read by user
        stoves = []
        for s in self.stoves:
            stoves.append(s.split(' ')[0])
        return stoves

    def fuel_types(self):
        '''Display fuel types captured in data'''

        # This function will produce a list of fuels found in the data set fuel_types) which is easily read by user
        fuels = []
        for f in self.fuels:
            fuels.append(f.split(' ')[0])
        return fuels

    def plot_stove(self, stove="All"):
        '''Must add .show() after calling function for plot to be generated'''

        # If no stove is specified in the input then all stoves will be plotted
        # If a stove is specified it must be input in a string and match a stove found in the dataset
        # This will output an interactive plot via a html which will only show up by adding .show() after calling it. 

        if type(stove) != str:
            raise ValueError('Must input stove type as a string!')

        stove_type = 0
        if stove == "All":
            stove_type = self.stoves
        else:
            for s in self.stoves:
                if stove in s:
                    stove_type = [s]
            if stove_type == 0:
                raise ValueError('Stove not found in data set.')

        fig = go.Figure()

        fig.update_yaxes(title_text="Temp")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text=stove + " Stove Temperature")

        for s in stove_type:
            fig.add_trace(go.Scatter(
                        x=self.df_stoves['Timestamp'],
                        y=self.df_stoves[s].values,
                        mode='lines',
                        name=s.split(' ')[0],
                        ))
        return fig

    def plot_fuel(self, fuel="All"):
        '''Must add .show() after calling function for plot to be generated'''

        # If no fuel is specified in the input then all fuels will be plotted
        # If a fuel is specified it must be input in a string and match a fuel found in the data set
        # This will output an interactive plot via a html which will only show up by adding .show() after calling it. 

        if type(fuel) != str:
            raise ValueError('Must input fuel type as a string!')

        fuel_type = 0
        if fuel == "All":
            fuel_type = self.fuels
        else:
            for f in self.fuels:
                if fuel in f:
                    fuel_type = [f]
            if fuel_type == 0:
                raise ValueError('Fuel not found in data set.')

        fig = go.Figure()

        fig.update_yaxes(title_text="Weight")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text=fuel + " Weight Readings")

        for f in fuel_type:
            fig.add_trace(go.Scatter(
                            x=self.df_stoves['Timestamp'],
                            y=self.df_stoves[f].values,
                            mode='lines',
                            name=f.split(' ')[0],
                            ))
        return fig

    def cooking_events(self, primary_threshold=15, time_between_events=60, stove="All"):
        ''' Cooking events for each stove'''

        # primary threshold should be the minimum temperature that you would like to consider to be a cooking event
        # time between events is the minimum time between cooking events
        # information on an individual stove can be called but it must be in the data set
        # if no stove is specified information will be retrieved for all stoves
        # this function will produce a dictionary with stove name and number of cooking events for each stove
        # this function will also create a self.cooking_events which will log the indices of the cooking event

        if type(stove) != str:
            raise ValueError('Must input fuel type as a string!')
        if type(time_between_events) != int or time_between_events < 0:
            raise ValueError("The time between events must be a positive integer!")
        if type(primary_threshold) != int or primary_threshold < 0:
            raise ValueError("The primary threshold must be a positive integer!")

        stove_type = 0
        if stove == "All":
            stove_type = self.stoves
        else:
            for s in self.stoves:
                if stove in s:
                    stove_type = [s]
        if stove_type == 0:
            raise ValueError('Stove not found in data set.')

        number_of_cooking_events = {}
        cook_events_list = {}

        for s in stove_type:
            peaks = find_peaks(self.df_stoves[s].values, height=primary_threshold, distance=time_between_events)[0]
            number_of_cooking_events.update({s.split(' ')[0]: len(peaks)})
            cook_events_list.update({s: peaks})
        self.cook_events = cook_events_list

        return number_of_cooking_events

    def plot_cooking_events(self, primary_threshold = 15, time_between_events = 60, stove="All"):
        '''Must add .show() after calling function for plot to be generated'''

        # The primary threshold must an integer >= 0
        # The time between cooking events must be an integer >= 0
        # The stove type must be entered as a string and must be in the data set
        # If the primary threshold and time between events is not specified it will revert back to default value even
        # if it was set to different values when calling cooking_events() function.

        if type(stove) != str:
            raise ValueError('Must input fuel type as a string!')
        if type(time_between_events) != int or time_between_events < 0:
            raise ValueError("The time between events must be a positive integer!")
        if type(primary_threshold) != int or primary_threshold < 0:
            raise ValueError("The primary threshold must be a positive integer!")

        stove_type = 0
        if stove == "All":
            stove_type = self.stoves
        else:
            for s in self.stoves:
                if stove in s:
                    stove_type = [s]
            if stove_type == 0:
                raise ValueError('Stove not found in data set.')

        self.cooking_events(primary_threshold, time_between_events, stove)
        events = self.cook_events
        fig = self.plot_stove(stove)

        for s in stove_type:
            fig.add_trace(
                go.Scatter(x=self.df_stoves['Timestamp'][events[s]],
                           y=self.df_stoves[s][events[s]],
                           mode='markers',
                           name=s.split(' ')[0] + 'Cooking Events'
                           )
                        )
        return fig


if __name__ == "__main__":

    # x = Household('./data_files/HH_38_2018-08-26_15-01-40_processed_v3.csv')

    # print(x.stove_types())
    # x.plot_cooking_events('telia')

    data_1 = Household('./data_files/test_4.csv')
    # print(data_1.cooking_events(primary_threshold= -5, time_between_events= 2, stove = "5"))
    data_1.plot_cooking_events(stove='telia')
