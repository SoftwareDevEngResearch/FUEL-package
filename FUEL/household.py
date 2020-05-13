import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks


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
    df_stoves, stoves, fuels = stove_info(data)
    return df_stoves, stoves, fuels


class Household:

    def __init__(self, dataframe, stoves, fuels, primary_threshold=15,  time_between_events=60):
        '''When called this class will verify that the input arguments are in the correct formats and set self values'''

        # First it will check that the dataframe is a dataframe and that the stoves and fuels are  in lists
        # It will then check to make sure that the stoves and fuels fed in are actually in the dataframe
        # The list of stoves and fuels should match column headers with the respective data in the dataframe

        if isinstance(dataframe, pd.DataFrame):
            pass
        else:
            raise ValueError("Must put in a dataframe!")
        if type(stoves) != list:
            raise ValueError('Must put in a list of stove types!')
        if type(fuels) != list:
            raise ValueError('Must put in a list of fuel types!')
        if type(time_between_events) != int or time_between_events < 0:
            raise ValueError("The time between events must be a positive integer!")
        if type(primary_threshold) != int or primary_threshold < 0:
            raise ValueError("The primary threshold must be a positive integer!")

        contents = dataframe.columns.values
        for s in stoves:
            if s not in contents:
                raise ValueError('One or more of the stove inputs were not found in the dataframe.')
        for f in fuels:
            if f not in contents:
                raise ValueError('One or more of the fuel inputs were not found in the dataframe.')

        self.df_stoves = dataframe
        self.stoves = stoves
        self.fuels = fuels
        self.primary_threshold = primary_threshold
        self.time_between_events = time_between_events


    def stove_types(self):
        ''' Display stove types captured in data'''

        return self.stoves

    def fuel_types(self):
        '''Display fuel types captured in data'''

        return self.fuels

    def check_stove_type(self, stove):
        '''This will check to see if the stove input is in dataset'''

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
        return stove_type

    def check_fuel_type(self, fuel):
        '''This will check if fuel input is in dataset'''

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
        return fuel_type

    def plot_stove(self, stove="All"):
        '''Must add .show() after calling function for plot to be generated'''

        # If no stove is specified in the input then all stoves will be plotted
        # If a stove is specified it must be input in a string and match a stove found in the dataset
        # This will output an interactive plot via a html which will only show up by adding .show() after calling it. 

        stove_type = self.check_stove_type(stove)

        fig = go.Figure()

        fig.update_yaxes(title_text="Temp")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text=stove + " Stove Temperature")

        for s in stove_type:
            fig.add_trace(go.Scatter(
                        x=self.df_stoves['timestamp'],
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

        fuel_type = self.check_fuel_type(fuel)

        fig = go.Figure()

        fig.update_yaxes(title_text="Weight")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text=fuel + " Weight Readings")

        for f in fuel_type:
            fig.add_trace(go.Scatter(
                            x=self.df_stoves['timestamp'],
                            y=self.df_stoves[f].values,
                            mode='lines',
                            name=f.split(' ')[0],
                            ))
        return fig

    def cooking_events(self, stove="All"):
        ''' Cooking events for each stove'''

        # primary threshold should be the minimum temperature that you would like to consider to be a cooking event
        # time between events is the minimum time between cooking events
        # information on an individual stove can be called but it must be in the data set
        # if no stove is specified information will be retrieved for all stoves
        # this function will produce a dictionary with stove name and number of cooking events for each stove
        # this function will also create a self.cooking_events which will log the indices of the cooking event

        if type(stove) != str:
            raise ValueError('Must input fuel type as a string!')

        stove_type = self.check_stove_type(stove)

        number_of_cooking_events = {}
        cook_events_list = {}

        for s in stove_type:
            peaks = find_peaks(self.df_stoves[s].values, height=self.primary_threshold, distance=self.time_between_events)[0]
            number_of_cooking_events.update({s: len(peaks)})
            cook_events_list.update({s: peaks})

        self.cook_events = cook_events_list

        return number_of_cooking_events

    def plot_cooking_events(self, stove="All"):
        '''Must add .show() after calling function for plot to be generated'''

        # The primary threshold must an integer >= 0
        # The time between cooking events must be an integer >= 0
        # The stove type must be entered as a string and must be in the data set
        # If the primary threshold and time between events is not specified it will revert back to default value even
        # if it was set to different values when calling cooking_events() function.

        if type(stove) != str:
            raise ValueError('Must input fuel type as a string!')


        stove_type = self.check_stove_type(stove)

        self.cooking_events(stove)
        events = self.cook_events
        fig = self.plot_stove(stove)

        for s in stove_type:
            fig.add_trace(
                go.Scatter(x=self.df_stoves['timestamp'][events[s]],
                           y=self.df_stoves[s][events[s]],
                           mode='markers',
                           name=s.split(' ')[0] + ' Cooking Events'
                           )
                        )
        return fig

    def fuel_usage(self, fuel_type, weight_threshold=0.2):
        '''Returns the total fuel used during testing period'''

        #NEEDS WORK

        if type(fuel_type) is not str:
            raise ValueError('Only one fuel may be put in at a time and it must be entered as a string.')

        fuel_type = self.check_fuel_type(fuel_type)

        fuel_usage = {}
        for i, fuel in enumerate(fuel_type):
            data = self.df_stoves[fuel]
            initial_weight = 0
            fuel_change = []
            for point in data:
                if abs(point-initial_weight) > weight_threshold:
                    initial_weight = point
                    fuel_change.append(point)

            total_usage = fuel_change[0]-fuel_change[-1]
            fuel_usage.update({fuel: total_usage})
        return fuel_usage

    def cooking_duration(self, stove="All"):
        '''This will return a datframe with the number of cooking minutes for each day for each stove.'''

        # First the cooking events must be pulled from the cooking_events() function.
        # To determine the duration of each cooking event the temperature information will be split at the location of
        # the cooking event. The first 0 temperature found before the cooking event will be assumed as the beginning
        # of the cooking event and the first zero temperature found after the cooking event will be assumed as the end
        # of the cooking event.
        # A day is classified as 24 hours (so day 1 is the first 24 hours after receiving the stove)
        # A dictionary will be returned with the key signifying the day and the value being how many minutes the
        # stove was used for during that period
        # Finally a dataframe will be compiled with the cooking durations for all stoves.

        stoves = self.cooking_events(stove)
        #list of all cooking events for each stove

        all_cooking_info = []

        for s in stoves:
            cooking_events_index = self.cook_events[s]
            cooking_temps = self.df_stoves[s]

            cooking_durations = []

            for i in cooking_events_index:
                # create two different list split at the located cooking event
                begin = cooking_temps[:i]
                end = cooking_temps[i:]
                # iterate backwards through the first half to find where it reaches 0
                for j, temp in enumerate(begin[::-1]):
                    if temp == 0:
                        start_time = i - j
                        break
                # iterate through the second half where it reaches 0
                for k, temp in enumerate(end):
                    if temp == 0:
                        end_time = i + k
                        break
                cooking_durations.append((start_time, end_time))

            day = 0
            daily_cooking = {}
            study_duration = (self.df_stoves['timestamp'].iloc[-1]-self.df_stoves['timestamp'][0]).days
            study_began = self.df_stoves['timestamp'][0]
            mins = 0
            for i, idx in enumerate(cooking_durations):
                end_time = self.df_stoves['timestamp'][idx[1]]
                start_time = self.df_stoves['timestamp'][idx[0]]
                days_since_start = (end_time - study_began).days
                if days_since_start != day:
                    day += 1
                    daily_cooking.update({day: mins})
                    mins = 0

                mins += (end_time-start_time).seconds/60

                if i == len(cooking_durations)-1:
                    day += 1
                    daily_cooking.update({day: mins})
            if len(daily_cooking) != study_duration:
                for i in range(study_duration):
                    day = i+1
                    if day not in daily_cooking:
                        mins = 0
                        daily_cooking.update({day: mins})

            all_cooking_info.append(daily_cooking)

        return pd.DataFrame(all_cooking_info, index=stoves)



if __name__ == "__main__":

    # x = Household('./data_files/HH_38_2018-08-26_15-01-40_processed_v3.csv')

    # print(x.stove_types())
    # x.plot_cooking_events('telia')

    #data_1 = Household('./data_files/test_datetime.csv')
    # print(data_1.cooking_events(primary_threshold= -5, time_between_events= 2, stove = "5"))
    #print(data_1.fuel_types())

    # print(data_1)
    #data_1.plot_stove().show()
    
    df, stoves, fuels = reformat_olivier_files('./data_files/test_datetime.csv')
    # print(df.columns.values)
    x = Household(df, stoves, fuels, time_between_events=30)
    # x.plot_fuel().show()
    # print(x.cooking_events())
    #x.plot_cooking_events().show()
    print(x.cooking_duration())
