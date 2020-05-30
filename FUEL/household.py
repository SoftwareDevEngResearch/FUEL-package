import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks


class Household:

    def __init__(self, dataframe, stoves, fuels, hh_id, temp_threshold=15, time_between_events=30, weight_threshold=0.2):
        '''Verifying that the input arguments are in the correct formats and set self values

        Args:
            dataframe (object): A dataframe containing sensor readings with timestamps formatted as datetime and column
                                headers that include only the name of the stove or fuel that is being measured.

            stoves (list): Stoves in the study (these should match the names of the column headers for the
                           stove information in the dataframe exactly).

            fuels (list): Fuels in the study (these should match the names of the column headers for the
                          fuel information in the dataframe exactly).

            hh_id (str): The individual household identification

            temp_threshold (int): A temperature threshold (degrees) for which all cooking events are identified.
                                  This value should be greater than or equal to zero. Defaults to 15.

            time_between_events (int): The time threshold (minutes) that will mark the minimum time between cooking
                                       events. This value should be greater than or equal to zero. Defaults to 30 mins.

            weight_threshold (float): The weight change (kg) that should be ignored. All weight changes above this
                                      value will be marked. Defaults to 0.2 kg.

        Returns:
            df_stoves : Input dataframe
            stoves : Input stoves
            fuels : Input fuels
            hh_id : Input Household ID
            temp_threshold: Input temperature threshold
            time_between_events: Input time between cooking events
            study_duration: The duration of the study in datetime format
            self.weight_threshold: Input weight threshold

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
        if type(temp_threshold) != int or temp_threshold < 0:
            raise ValueError("The temperature threshold must be a positive integer!")
        if type(weight_threshold) != float or weight_threshold < 0:
            raise ValueError("The weight threshold must be a positive number!")

        contents = dataframe.columns.values
        for s in stoves:
            if s not in contents:
                raise ValueError(s + ' stove not found in the dataframe.')
        for f in fuels:
            if f not in contents:
                raise ValueError(f + ' fuel not found in the dataframe.')

        self.df_stoves = dataframe.applymap(lambda i: i.lower() if type(i) == str else i)
        self.stoves = [i.lower() for i in stoves]
        self.fuels = [i.lower() for i in fuels]
        self.hh_id = hh_id
        self.temp_threshold = temp_threshold
        self.time_between_events = time_between_events
        self.study_duration = self.df_stoves['timestamp'].iloc[-1] - self.df_stoves['timestamp'][0]
        self.weight_threshold = weight_threshold

    def check_stove_type(self, stove="All"):
        '''Check if stove input is in dataset

        Args:
            stove (string): If only looking at one stove, stove must be input as a str. If looking at
                            multiple stoves, stoves must be input as a list of stoves. Defaults all stoves
                            in data set.

        Returns:
            stove_type (list) : If stove(s) are found in the original list of stoves in the dataframe then it returns
                                a list containing the stove(s).

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
                    raise ValueError(s + ' not found in data set.')

            if not stove_type:
                raise ValueError('Stove not found in data set.')
        return stove_type

    def check_fuel_type(self, fuel="All"):
        '''Check if fuel input is in dataset

        Args:
            fuel (string): The name of the fuel(s) that is being checked for. If multiple fuels are desired they must
                            be input as a list of stings.

        Returns:
            fuel_type (list) : If all fuels are found in the original list of stoves in the dataframe then it returns
                                a list of the fuels.

        '''

        if type(fuel) == list:
            for f in fuel:
                if type(f) != str:
                    raise ValueError('Must input all fuels as strings!')
        elif type(fuel) == str:
            fuel = [fuel]
        elif type(fuel) != str:
            raise ValueError('Must input fuel type as string!')

        fuel_type = []
        if fuel[0] == "All":
            fuel_type = self.fuels
        else:
            for f in fuel:
                if f in self.fuels:
                    fuel_type.append(f)
            if not fuel_type:
                raise ValueError('Fuel not found in data set.')
        return fuel_type

    def cooking_events(self, stove="All"):
        ''' Determine the number of cooking events on each stove during study.

        Args:
            stove (str): If only looking at one stove, stove must be input as a str. If looking at
                         multiple stoves, stoves must be input as a list of stoves. Defaults all stoves
                         in data set.

        Returns:
            cook_events (dict) : A dictionary containing each stove as a key and a list of all indices of determined
                                cooking events in the data as the values. This is used internally by other functions.

            number_of_cooking_events (dict) : A dictionary containing each stove as a key and the number of cooking
                                              events on that stove as the values.

        '''

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
    #
    # def _find_significant_weight_changes(self, fuel, peaks):
    #     '''Find all significant weight changes (internal function).
    #
    #     Args:
    #         fuel (str) : name of fuel in data set
    #
    #         peaks (list): A list of all fuel change indices found in the data set.
    #
    #     Returns:
    #         weight_change (list): A list of all fuel change indices found that resulted in a change of fuel weight
    #                                    larger than the prescribed threshold (weight_threshold).
    #              '''
    #     fuel_data = list(self.df_stoves[fuel])
    #
    #     weight = fuel_data[peaks[0]]
    #     weight_change = [peaks[0]]
    #
    #     # if the weight difference between these peaks is less than the weight threshold ignore it
    #     for i in peaks[1:]:
    #         new_weight = fuel_data[i]
    #         weight_before = fuel_data[i-1]
    #         weight_after = fuel_data[i+1]
    #         weight_diff = new_weight - weight
    #
    #         if abs(weight_diff) < self.weight_threshold:
    #             pass
    #
    #         else:
    #             # check to make sure it isnt catching random peaks
    #             if weight_diff > self.weight_threshold:
    #                 if abs(weight_after-weight_before) < self.weight_threshold or weight_after < weight_before:
    #                     pass
    #                 else:
    #                     weight_change.append(i)
    #                     weight = fuel_data[i]
    #             else:
    #                 weight_change.append(i)
    #                 weight = fuel_data[i]
    #
    #         # to make sure that the lowest value is captured check the final weight value against the previous
    #         if i == peaks[-1]:
    #             last_idx = len(fuel_data) - 1
    #             last_weight = fuel_data[last_idx]
    #             if last_weight < weight:
    #                 weight_change.append(last_idx)
    #     return weight_change

    def _find_weight_changes(self, fuel):
        '''Find all significant weight changes (internal function).

        Args:
            fuel (str) : name of fuel in data set

        Returns:
            weight_change (list): A list of all fuel change indices found that resulted in a change of fuel weight
                                       larger than the prescribed threshold (weight_threshold).
        '''

        fuel_data = list(self.df_stoves[fuel])

        weight = fuel_data[0]
        weight_changes = []

        for i, current_weight in enumerate(fuel_data[1:]):
            if fuel == "lpg" and current_weight < 2: # should change this to be more versatile later
                pass
            else:
                if i == len(fuel_data)-2:
                    if fuel_data[i] < weight:
                        weight_changes.append(i+1)
                else:
                    weight_before = fuel_data[i]
                    weight_after = fuel_data[i+2]
                    weight_diff = current_weight - weight

                    if abs(weight_diff) < self.weight_threshold:
                        pass
                    else:
                        # check to make sure it isnt catching random peaks
                        if weight_diff > self.weight_threshold:
                            if abs(weight_after-weight_before) < self.weight_threshold or weight_after < weight_before:
                                pass
                            else:
                                weight_changes.append(i+1)
                                weight = current_weight
                        else:
                            weight_changes.append(i+1)
                            weight = current_weight
        return weight_changes

    def _daily_fuel_use(self, fuel, weight_changes):
        '''Determine amount of fuel used in each 24hr period of study (Internal function).

        Args:
            fuel (str): Name of fuel in dataset.

            weight_changes (list): List of indices of all significant fuel changes for chosen fuel.

        Returns:
            daily_fuel_usage (dict): A dictionary containing fuel usage information for each day of study. Keys
                                         represent the day of the study, values is the total weight change (kg) recorded
                                         for that day of the study.
        '''

        daily_fuel_usage = {}
        fuel_info = self.df_stoves[fuel]
        day = 0
        study_began = self.df_stoves['timestamp'][0]
        study_duration = round(self.study_duration.total_seconds()/86400) # rounding to the nearest day
        weight = fuel_info[weight_changes[0]]
        weight_diff = 0
        for i in weight_changes[1:]:

            day_of_use = (self.df_stoves['timestamp'][i] - study_began).days

            new_weight = fuel_info[i]

            if weight - new_weight < 0:
                # indicates an adding of fuel not a fuel usage
                pass

            else:

                if day_of_use == study_duration:
                    # fuel used on final day of study
                    if weight - new_weight < self.weight_threshold:
                        weight_diff = 0
                    else:
                        weight_diff = weight - new_weight
                    daily_fuel_usage.update({day_of_use: weight_diff})

                elif day_of_use == day:
                    weight_diff += weight - new_weight
                    daily_fuel_usage.update({day+1: weight_diff})

                else:
                    weight_diff = weight - new_weight
                    day = day_of_use

                    daily_fuel_usage.update({day+1: weight_diff})

            weight = new_weight

        if len(daily_fuel_usage) != study_duration:
            for i in range(study_duration):
                day = i + 1
                if day not in daily_fuel_usage:
                    weight = 0
                    daily_fuel_usage.update({day: weight})

        return daily_fuel_usage

    def fuel_usage(self, fuel="All", min_fuel=2):
        '''Determine the total amount of each fuel used on each day of the study.

        Args:
            fuel (string): If only looking at one fuel, fuel must be input as a str. If looking at
                         multiple fuels, fuels must be input as a list of fuels. Defaults all fuels
                         in data set.

            min_fuel(int): The minimum weight(kg) that you want to have weight be recognized
        Returns:
            self.weight_changes (dict): A dictionary of all significant fuel changes in study. Key is the fuel type,
                                        values are lists of indices where significant fuel changes took place. This is
                                        used by another function internally.

            Daily fuel usage (dataframe): A dataframe, rows = fuel types, columns = day (24hr period) of study,
                                          values are the amount of fuel (kg) used in that day of study.
        '''

        fuel_type = self.check_fuel_type(fuel)

        fuel_change = []
        fuel_weight_changes = {}  # will be used in other functions
        for f in fuel_type:
            # peaks = find_peaks(self.df_stoves[f].values, height=min_fuel, distance=1)[0]
            # weight_changes = self._find_significant_weight_changes(f, peaks)
            changes = self._find_weight_changes(f)
            fuel_weight_changes.update({f: changes})
            daily_usage = self._daily_fuel_use(f, changes)
            fuel_change.append(daily_usage)

        self.weight_changes = fuel_weight_changes
        fuel_use = pd.DataFrame(fuel_change, index=fuel_type).transpose()
        return fuel_use.sort_index(ascending=True)

    def _find_cooking_durations_idx(self, stove):
        ''' Determine the indices of the start and end of each cooking event (internal function).

        Args:
            stove (str): Name of a cook stove in data set.

        Returns:
            cooking_events_list (list) : A list of tuples containing the indices of the beginning and end of a
                                             cooking event [(cooking begins, cooking ends)].

        '''

        cooking_events_index = self.cook_events[stove]
        cooking_temps = self.df_stoves[stove]

        cooking_event_list = []

        for i in cooking_events_index:
            # create two different list split at the located cooking event
            begin = cooking_temps[:i]
            end = cooking_temps[i:]
            start_time = False
            end_time = False
            # iterate backwards through the first half to find where it reaches designated cooking temp threshold
            for j, temp in enumerate(begin[::-1]):
                if temp < self.temp_threshold:
                    start_time = i - j
                    break
            # iterate through the second half where it reaches designated cooking temp threshold
            for k, temp in enumerate(end):
                if temp < self.temp_threshold:
                    end_time = i + k
                    break
            if not start_time:
                raise ValueError('Could not find start time for cooking event on ' + stove + ' at index: ', i)
            if not end_time:
                raise ValueError('Could not find end time for cooking event on ' + stove + ' at index: ', i)

            cooking_event_list.append((start_time, end_time))

        return cooking_event_list

    def _daily_cooking_time(self, cooking_durations_list):
        '''Determine the total time spent cooking on a stove (mins) for each day of the study (internal function).

        Args:
            cooking_duration_list (list): A list of tuples containing the indices of the beginning and end of a
                                          cooking event [(cooking begins, cooking ends)].

        Returns:
                daily_cooking (dict): A dictionary containing stove cooking information for each day of study. Keys
                                      represent the day of the study, values are the total time(min) cooking recorded
                                      for that day of the study.

        '''

        day = 0
        daily_cooking = {}
        study_duration = round(self.study_duration.total_seconds()/86400) # rounding to the nearest day
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

            mins += (end_time - start_time).seconds / 60

            if i == len(cooking_durations_list) - 1:
                day += 1
                daily_cooking.update({day: mins})

        if len(daily_cooking) != study_duration:
            for i in range(study_duration):
                day = i + 1
                if day not in daily_cooking:
                    mins = 0
                    daily_cooking.update({day: mins})

        return daily_cooking

    def cooking_duration(self, stove="All"):
        '''Determines the cooking duration (mins) on each stove for each day of the study.

        Args:
            stove (str): If only looking at one stove, stove must be input as a str. If looking at
                         multiple stoves, stoves must be input as a list of stoves. Defaults all stoves
                         in data set.
        Returns:
            Cooking Durations (dataframe):  A dataframe, rows = stove type, columns = day of study, value duration
                                            of cooking (mins) on a stove during that day of the study.

        '''

        stoves = self.cooking_events(stove)
        all_cooking_info = []

        for s in stoves:
            cooking_durations_list = self._find_cooking_durations_idx(s)
            daily_cooking = self._daily_cooking_time(cooking_durations_list)

            all_cooking_info.append(daily_cooking)
        cooking_times = pd.DataFrame(all_cooking_info, index=stoves).transpose()
        return cooking_times.sort_index(ascending=True)

    def plot_stove(self, stove="All", cooking_events=False):
        '''Plotting the temperature data of stoves over duration of study.

        Args:
            stove (str): If only plotting one stove temperature readings stove must be input as a str. If plotting
                         multiple stoves, stoves must be input as a list of stoves. Defaults to plotting all stoves
                         in data set.
            cooking_events (bool): If it is desired to have cooking events marked cooking_events must be set to
                                   True. Default is False and will only show the cook stove temperature data with no
                                   cooking events marked.

        Returns:
              figure : Returns interactive line plots of all requested stove temperature readings over the
                       duration of the study. If cooking_events = True plot will show determined cooking events with
                       a point.
        '''

        stove_type = self.check_stove_type(stove)

        fig = go.Figure()

        fig.update_yaxes(title_text="Temp")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text="Household: " + hh_id + " " + stove + " Stove Temperature")


        for s in stove_type:
            fig.add_trace(go.Scatter(
                x=self.df_stoves['timestamp'],
                y=self.df_stoves[s].values,
                mode='lines',
                name=s.split(' ')[0],
            ))

        if cooking_events:
            self.cooking_events(stove)
            events = self.cook_events

            for s in stove_type:
                fig.add_trace(
                    go.Scatter(x=self.df_stoves['timestamp'][events[s]],
                               y=self.df_stoves[s][events[s]],
                               mode='markers',
                               name=s + ' Cooking Events'
                               )
                )
        return fig.show()

    def plot_fuel(self, fuel="All", fuel_usage=False):
        '''Plotting the fuel weight data over duration of study.

        Args:
            fuel (str): If only plotting one fuel weight data fuel must be input as a string. If plotting
                         multiple fuels, fuels must be input as a list of fuels. Defaults to plotting all fuels
                         in data set.
            fuel_usage (bool): If it is desired to have fuel usage marked fuel_usage must be set to True.
                               Default is False and will only show the fuel weight data with no weight changes marked.

        Returns:
            figure : Returns interactive line plots of all requested fuel weight data over the
                     duration of the study. If fuel_usage=True all significant fuel weight changes will be
                     marked on the plot.
        '''

        fuel_type = self.check_fuel_type(fuel)

        fig = go.Figure()

        fig.update_yaxes(title_text="Weight")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text="Household: " + hh_id + " " + fuel + " Weight Readings")

        for f in fuel_type:
            fig.add_trace(
                go.Scatter(
                    x=self.df_stoves['timestamp'],
                    y=self.df_stoves[f].values,
                    mode='lines',
                    name=f.split(' ')[0],
                ))

        if fuel_usage:
            self.fuel_usage(fuel=fuel_type)
            changes = self.weight_changes

            for f in fuel_type:
                fig.add_trace(
                    go.Scatter(x=self.df_stoves['timestamp'][changes[f]],
                               y=self.df_stoves[f][changes[f]],
                               mode='markers',
                               name=f + ' Weight Change'
                               )
                )
        return fig.show()


if __name__ == "__main__":
    from olivier_file_convert import reformat_olivier_files as reformat

    filepaths = ['HH_38_2018-08-26_15-01-40_processed_v3.csv', # look at the lpg
             'HH_44_2018-08-17_13-49-22_processed_v2.csv',
             'HH_141_2018-08-17_17-50-31_processed_v2.csv', #lpg is off here too
             'HH_318_2018-08-25_18-35-07_processed_v2.csv',
             'HH_319_2018-08-25_19-27-32_processed_v2.csv',
             'HH_326_2018-08-25_17-52-16_processed_v2.csv',
             'HH_345_2018-08-25_15-52-57_processed_v2.csv',
             'HH_371_2018-08-17_15-31-52_processed_v2.csv'
             ]

    for file in filepaths:
        df, stoves, fuels, hh_id = reformat('./data_files/' + file)
        x = Household(df, stoves, fuels, hh_id)
        print(file, '\n',
            # x.check_stove_type(),
            # x.check_fuel_type('lpg')
            # x.cooking_events()
            x.fuel_usage() #, '\n',
            # x.cooking_duration()
            # x.df_stoves
            # x.study_duration.total_seconds()/86400
        )
        x.plot_fuel(fuel_usage=True)

    # df, stoves, fuels, hh_id = reformat('./data_files/HH_38_2018-08-26_15-01-40_processed_v3.csv')
    # x = Household(df, stoves, fuels, hh_id)
    # print(x.fuel_usage('firewood'))
    # x.plot_fuel(fuel_usage=True)

