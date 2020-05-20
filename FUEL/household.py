import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks


class Household:

    def __init__(self, dataframe, stoves, fuels, temp_threshold=15,  time_between_events=30):
        '''When called this class will verify that the input arguments are in the correct formats and set self values

        Args:
            dataframe (object): A dataframe containing sensor readings with timestamps formatted as datetime and column
                                headers that include only the name of the stove or fuel that is being measured.

            stoves (list): Stoves in the study (these should match the names of the column headers for the
                           stove information in the dataframe exactly).

            fuels (list): Fuels in the study (these should match the names of the column headers for the
                          fuel information in the dataframe exactly).

            temp_threshold (int): A temperature threshold (degrees) for which all cooking events are identified.
                                  This value should be greater than or equal to zero.

            time_between_events (int): The time threshold (minutes) that will mark the minimum time between cooking
                                       events. This value should be greater than or equal to zero.

        Returns:
            df_stoves : Input dataframe
            stoves : Input stoves
            fuels : Input fuels
            temp_threshold: Input temperature threshold
            time_between_events: Input time between cooking events
            study_duration: The duration of the study in datetime format

        '''

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
        if type(temp_threshold
                ) != int or temp_threshold\
                < 0:
            raise ValueError("The temperature threshold must be a positive integer!")

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
        self.temp_threshold = temp_threshold
        self.time_between_events = time_between_events
        self.study_duration = self.df_stoves['timestamp'].iloc[-1]-self.df_stoves['timestamp'][0]

    def check_stove_type(self, stove="All"):
        '''Check if stove input is in dataset

        Args:
            stove (string): The name of the stove(s) that is being checked for. If multiple stoves are desired they must
                            be input as a list of stings.

        Returns:
            stove_type (list) : If stove(s) are found in the original list of stoves in the dataframe then it returns
                                a list of the stoves.

        '''
        if type(stove) == list:
            for s in stove:
                if type(s) != str:
                    raise ValueError('Must input all stoves as strings!')
        elif type(stove) != str:
            raise ValueError('Must input stove type as string!')

        stove_type = []
        if stove == "All":
            stove_type = self.stoves
        else:
            for s in stove:
                if s in self.stoves:
                    stove_type.append(s)
                else:
                    raise ValueError(s+' not found in data set.')

            if not stove_type:
                raise ValueError('Stove not found in data set.')
        return stove_type

    def check_fuel_type(self, fuel="All"):
        '''Check if fuel input is in dataset

        Args:
            fuel (string): The name of the stove(s) that is being checked for.

        Returns:
            stove_type (list) : If all stoves are found in the original list of stoves in the dataframe then it returns
                                a list of the stoves.

        '''

        if type(fuel) == list:
            for f in fuel:
                if type(f) != str:
                    raise ValueError('Must input all fuels as strings!')
                else:
                    raise ValueError(f+' not found in data set.')
        elif type(fuel) != str:
            raise ValueError('Must input fuel type as string!')

        fuel_type = []
        if fuel == "All":
            fuel_type = self.fuels
        else:
            for f in fuel:
                if f in self.fuels:
                    fuel_type.append(f)
            if not fuel_type:
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

        # temperature threshold should be the minimum temperature that you would like to consider to be a cooking event
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
            peaks = find_peaks(self.df_stoves[s].values, height=self.temp_threshold
                               , distance=self.time_between_events)[0]
            number_of_cooking_events.update({s: len(peaks)})
            cook_events_list.update({s: peaks})

        self.cook_events = cook_events_list

        return number_of_cooking_events

    def plot_cooking_events(self, stove="All"):
        '''Must add .show() after calling function for plot to be generated'''

        # The temperature threshold must an integer >= 0
        # The time between cooking events must be an integer >= 0
        # The stove type must be entered as a string and must be in the data set
        # If the temperature threshold and time between events is not specified it will revert back to default value even
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
                           name=s + ' Cooking Events'
                           )
                        )
        return fig

    def fuel_usage(self, fuel = "All", weight_threshold=0.1):
        '''Returns the total of each fuel used on each day of the study.'''

        # Should input which stoves you are interested in and the weight threshold
        # weight threshold is the weight (kg) change that yu would like to ignore
        # returns a dataframe with all of the selected fuels and how much of each fuel was used each day.

        if type(fuel) is not str:
            raise ValueError('Only one fuel may be put in at a time and it must be entered as a string.')

        fuel_type = self.check_fuel_type(fuel)

        def find_significant_changes(peaks):
            '''This function finds all changes in weight that exceed the threshold. '''

            weight = self.df_stoves[f][peaks[0]]
            weight_change = [peaks[0]]

            # if the weight difference between these peaks is less than the weight threshold ignore it
            for i in peaks[1:]:
                new_weight = self.df_stoves[f][i]
                if abs(new_weight - weight) < weight_threshold:
                    pass
                else:
                    weight_change.append(i)
                    weight = self.df_stoves[f][i]

                # to make sure that the lowest value is captured check the final weight value against the previous
                # recorded weight
                if i == peaks[-1]:
                    last_idx = len(self.df_stoves[f])-1
                    last_weight = self.df_stoves[f][last_idx]
                    if last_weight < weight:
                        weight_change.append(last_idx)
            return weight_change

        def daily_fuel_use(fuel, weight_changes):
            '''Determines How much of a fuel was used in each day of the study.'''

            daily_fuel_usage = {}
            day = 1
            study_began = self.df_stoves['timestamp'][0]
            study_duration = self.study_duration.days
            initial_weight = self.df_stoves[fuel][weight_changes[0]]
            new_weight = 0
            weight_diff = 0

            for i in weight_changes:
                if (self.df_stoves['timestamp'][i]-study_began).days == day-1:
                    new_weight = self.df_stoves[fuel][i]
                    weight_diff = initial_weight - new_weight
                    daily_fuel_usage.update({day: weight_diff})
                else:
                    day += 1
                    weight_diff = new_weight - self.df_stoves[fuel][i]
                    daily_fuel_usage.update({day: weight_diff})

            if len(daily_fuel_usage) != study_duration:
                for i in range(study_duration-1):
                    day = i+2
                    if day not in daily_fuel_usage:
                        mins = 0
                        daily_fuel_usage.update({day: mins})

            return daily_fuel_usage

        fuel_change = []

        for f in fuel_type:
            peaks = find_peaks(self.df_stoves[f].values, height=1, distance=1)[0]
            weight_changes = find_significant_changes(peaks)
            daily_usage = daily_fuel_use(f, weight_changes)
            fuel_change.append(daily_usage)

        return pd.DataFrame(fuel_change, index=fuel_type)

    def cooking_duration(self, stove="All"):
        '''This will return a data frame with the number of cooking minutes for each day for each stove.'''

        # First the total cooking duration for each event on each stove will be determined.
        # Then the total cooking duration for each day on each stove will be determined
        # Finally a data frame will be produced that contains this information.

        def cooking_durations(cooking_events_index, cooking_temps):
            ''' This will return a list of the beginning and end time for every identified cooking event on a stove.'''

            # Takes in the index of each identified cooking event and the recorded temperature for that stove
            # Finds the beginning and end of cooking event by finding the lowest temperatures on each side of the event.
            cooking_event_list = []

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
                cooking_event_list.append((start_time, end_time))

            return cooking_event_list

        def daily_cooking_time(cooking_durations_list):
            '''This will return the total cooking time on a stove for each 24 hour period of study.'''

            # Takes in the list of cooking event durations
            # Determines the length of each cooking event and which day of the study it occurred on.
            # Adds the duration of cooking time to a dictionary associated with the correct day.
            # If no cooking was recorded on a stove during a day it will add a 0 value entry to dictionary for that day.

            day = 0
            daily_cooking = {}
            study_duration = self.study_duration.days
            study_began = self.df_stoves['timestamp'][0]
            mins = 0

            for i, idx in enumerate(cooking_durations_list):
                end_time = self.df_stoves['timestamp'][idx[1]]
                start_time = self.df_stoves['timestamp'][idx[0]]
                days_since_start = (end_time - study_began).days
                if days_since_start != day:
                    day += 1
                    daily_cooking.update({day: mins})
                    mins = 0

                mins += (end_time-start_time).seconds/60

                if i == len(cooking_durations_list)-1:
                    day += 1
                    daily_cooking.update({day: mins})

            if len(daily_cooking) != study_duration:
                for i in range(study_duration):
                    day = i+1
                    if day not in daily_cooking:
                        mins = 0
                        daily_cooking.update({day: mins})

            return daily_cooking

        stoves = self.cooking_events(stove)
        all_cooking_info = []

        for s in stoves:
            cooking_events_index = self.cook_events[s]
            cooking_temps = self.df_stoves[s]

            cooking_durations_list = cooking_durations(cooking_events_index, cooking_temps)
            daily_cooking = daily_cooking_time(cooking_durations_list)

            all_cooking_info.append(daily_cooking)

        return pd.DataFrame(all_cooking_info, index=stoves)


if __name__ == "__main__":

    from olivier_file_convert import reformat_olivier_files as reformat

    # example file
    df, stoves, fuels = reformat('./data_files/HH_38_2018-08-26_15-01-40_processed_v3.csv')

    x = Household(df, stoves, fuels)

    print(x.check_fuel_type(['firewod', 'lpg']))

