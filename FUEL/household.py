import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import find_peaks


class Household:

    def __init__(self, dataframe, stoves, fuels, hh_id, temp_threshold=15, time_between_events=60, min_cooktime=15,
                 weight_threshold=0.2):
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
                                       events. This value should be greater than or equal to zero. Defaults to 60 mins.

            min_cook_time (int): The minimum cooking time (mins). Default value of 15 mins.

            weight_threshold (float): The weight change (kg) that should be ignored. All weight changes above this
                                      value will be marked. Defaults to 0.2 kg.

        Returns:
            df_stoves : Input dataframe
            stoves : Input stoves
            fuels : Input fuels
            hh_id : Input Household ID
            temp_threshold: Input temperature threshold
            time_between_events: Input time between cooking events
            min_cook_time : Input min cooking time
            study_duration: The duration of the study in datetime format
            weight_threshold: Input weight threshold

        '''

        if isinstance(dataframe, pd.DataFrame):
            pass
        else:
            raise ValueError("Must put in a dataframe!")
        if type(stoves) != list:
            raise ValueError('Must put in a list of stove types!')
        if type(fuels) != list:
            raise ValueError('Must put in a list of fuel types!')
        if type(hh_id) != str:
            raise ValueError('Must put in household ID as a string!')
        if type(time_between_events) != int or time_between_events < 0:
            raise ValueError("The time between events must be a positive integer!")
        if type(temp_threshold) != int or temp_threshold < 0:
            raise ValueError("The temperature threshold must be a positive integer!")
        if type(min_cooktime) != int or min_cooktime < 0:
            raise ValueError("The minimum cooking time must be a positive integer!")
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
        self.min_cooktime = min_cooktime
        self.study_duration = self.df_stoves['timestamp'].iloc[-1] - self.df_stoves['timestamp'][0]
        self.study_days = round(self.study_duration.total_seconds()/86400) # rounding to the nearest day
        self.weight_threshold = weight_threshold

    def _check_item(self, item):
        '''Check if stove or fuel input is in dataset

        Args:
            item (string): If only looking at one item, it must be input as a str. If looking at
                            multiple items, they must be input as a list of items.
        Returns:
            item_type (list) : If items are found in the stove list it will return a list of stoves. If items are found
                                in the fuel list it will return a list of fuels. If items are found in neither or both
                                stove and fuel lists it will return an error.

        '''
        item_type = []
        stove = False
        fuel = False

        if item == "All Stoves":
            item_type = self.stoves
        elif item == "All Fuels":
            item_type = self.fuels
        else:
            if type(item) != list:
                item = [item]
            for i in item:
                if type(i) != str:
                    raise ValueError('Must input all items as strings!')
                if i in self.stoves:
                    item_type.append(i)
                    stove = True
                if i in self.fuels:
                    item_type.append(i)
                    fuel = True
                if stove and fuel:
                    raise ValueError('Put in only fuel or stoves not both!')
                if not stove and not fuel:
                    raise ValueError(i + " was not found in dataset.")
        return item_type

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
            if fuel == "lpg" and current_weight < 5:  # should change this to be more versatile later
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
        weight = fuel_info[weight_changes[0]]
        weight_diff = 0
        total_fuel_usage = 0
        for i in weight_changes[1:]:
            day_of_use = (self.df_stoves['timestamp'][i] - study_began).days
            new_weight = fuel_info[i]
            if weight - new_weight < self.weight_threshold:
                # indicates an adding of fuel not a fuel usage
                pass
            else:
                total_fuel_usage += weight - new_weight
                if day_of_use == self.study_days:
                    if day_of_use in daily_fuel_usage:
                        weight_diff += weight - new_weight
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

        if len(daily_fuel_usage) != self.study_days:
            for i in range(self.study_days):
                day = i + 1
                if day not in daily_fuel_usage:
                    weight = 0
                    daily_fuel_usage.update({day: weight})

        daily_fuel_usage.update({0: total_fuel_usage})

        return daily_fuel_usage

    def fuel_usage(self, fuel="All Fuels"):
        '''Determine the total amount of each fuel used on each day of the study.

        Args:
            fuel (string): If only looking at one fuel, fuel must be input as a str. If looking at
                         multiple fuels, fuels must be input as a list of fuels. Defaults all fuels
                         in data set.

        Returns:
            self.weight_changes (dict): A dictionary of all significant fuel changes in study. Key is the fuel type,
                                        values are lists of indices where significant fuel changes took place. This is
                                        used by another function internally.

            Daily fuel usage (dataframe): A dataframe, rows = fuel types, columns = day (24hr period) of study,
                                          values are the amount of fuel (kg) used in that day of study.
        '''

      
        fuel_type = self._check_item(fuel)

        fuel_change = []
        fuel_weight_changes = {}  # will be used in other functions
        for f in fuel_type:
            changes = self._find_weight_changes(f)
            fuel_weight_changes.update({f: changes})
            daily_usage = self._daily_fuel_use(f, changes)
            fuel_change.append(daily_usage)

        self.weight_changes = fuel_weight_changes
        fuel_use = pd.DataFrame(fuel_change, index=fuel_type).transpose()
        return fuel_use.sort_index(ascending=True)

    def cooking_events(self, stove="All Stoves"):
        ''' Determine the number of cooking events on each stove during study.

        Args:
            stove (str): If only looking at one stove, stove must be input as a str. If looking at
                         multiple stoves, stoves must be input as a list of stoves. Defaults all stoves
                         in data set.

        Returns:
            cook_events (dict) : A dictionary containing each stove as a key and a list of lists containing cooking
                                event information [cooking event, start of cooking, end of cooking] as the values

          '''

        stove_type = self._check_item(stove)
        cook_events = {}

        for s in stove_type:
            stove_temps = self.df_stoves[s]
            possible_cooking_events = find_peaks(stove_temps, height=self.temp_threshold
                               , distance=self.time_between_events)[0]
            events = []
            for i in possible_cooking_events:
                before_event = stove_temps[:i]
                after_event = stove_temps[i:]
                start_time = False
                end_time = False
                min_below_threshold = 0
                for j, temp in enumerate(before_event[::-1]):
                    if j == len(before_event)-2:
                        start_time = 0
                        min_below_threshold = 0
                        break
                    elif temp < self.temp_threshold:
                        min_below_threshold += 1
                        if min_below_threshold == 5:
                            start_time = i - j
                            min_below_threshold = 0
                            break
                    else:
                        min_below_threshold = 0
                for k, t in enumerate(after_event):
                    if k == len(after_event)-2:
                        end_time = len(stove_temps)-1
                        break
                    elif t < self.temp_threshold:
                        min_below_threshold += 1
                        if min_below_threshold == 5:
                            end_time = i + k
                            break
                    else:
                        min_below_threshold = 0
                if not start_time:
                    raise ValueError('Could not find start time for cooking event on ' + stove + ' at index: ', i)
                if not end_time:
                    raise ValueError('Could not find end time for cooking event on ' + stove + ' at index: ', i)
                if events:
                    previous_event = events[-1]
                    if previous_event[1] == start_time:
                        pass
                    if previous_event[2] > start_time:
                        start_time = previous_event[2] + 1
                    else:
                        events.append([i, start_time, end_time])
                else:
                    events.append([i, start_time, end_time])
            cook_events.update({s: events})
        return cook_events

    def _daily_cooking_time(self, cooking_events):
        '''Determine the total time spent cooking on a stove (mins) for each day of the study (internal function).

        Args:
            cooking_events(list): a list of lists containing cooking event information [cooking event, start
                                          of cooking, end of cooking] as the values

        Returns:
                daily_cooking (dict): A dictionary containing stove cooking information for each day of study. Keys
                                      represent the day of the study, values are the total time(min) cooking recorded
                                      for that day of the study. Day 0 represents the total amount of cooking time.

        '''

        day = 0
        daily_cooking = {}
        study_began = self.df_stoves['timestamp'][0]
        daily_mins = 0
        total_mins= 0

        for i in cooking_events:
            for j, idx in enumerate(cooking_events[i]):
                end_time = self.df_stoves['timestamp'][idx[2]]
                start_time = self.df_stoves['timestamp'][idx[1]]
                days_since_start = (end_time - study_began).days
                total_mins += (end_time - start_time).seconds / 60
                if days_since_start != day:
                    daily_cooking.update({day+1: daily_mins})
                    day = days_since_start
                    daily_mins = (end_time - start_time).seconds / 60
                    if j == len(cooking_events[i]) - 1:
                        if days_since_start == self.study_days:
                            day = days_since_start
                        else:
                            day += 1
                        daily_cooking.update({day: daily_mins})
                        break
                elif j == len(cooking_events[i]) - 1:
                    daily_mins += (end_time - start_time).seconds / 60
                    if days_since_start == self.study_days:
                        day = days_since_start
                    else:
                        day += 1
                    daily_cooking.update({day: daily_mins})
                else:
                    daily_mins += (end_time - start_time).seconds / 60
            if len(daily_cooking) != self.study_days:
                for i in range(self.study_days):
                    day = i + 1
                    if day not in daily_cooking:
                        mins = 0
                        daily_cooking.update({day: mins})

            daily_cooking.update({0: total_mins})

        return daily_cooking

    def cooking_duration(self, stove="All Stoves"):
        '''Determines the cooking duration (mins) on each stove for each day of the study.

        Args:
            stove (str): If only looking at one stove, stove must be input as a str. If looking at
                         multiple stoves, stoves must be input as a list of stoves. Defaults all stoves
                         in data set.
        Returns:
            Cooking Durations (dataframe):  A dataframe, rows = stove type, columns = day of study, value duration
                                            of cooking (mins) on a stove during that day of the study.

        '''
        stove_type = self._check_item(stove)
        all_cooking_info = []

        for s in stove_type:
            daily_cooking = self._daily_cooking_time(self.cooking_events(s))

            all_cooking_info.append(daily_cooking)

        cooking_times = pd.DataFrame(all_cooking_info, index=stove_type).transpose()

        return cooking_times.sort_index(ascending=True)

    def _color_assignment(self, item):
        '''Temporary means of assigning colors.'''

        colors = {}
        color_list = ['#F5793A', '#A95AA1', '#0F2080', '#85C0F9']
        for color, i in enumerate(item):
            colors.update({i: color_list[color]})
        
        return colors

    def plot_stove(self, stove="All Stoves", cooking_events=False):
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

        stove_type = self._check_item(stove)

        colors = self._color_assignment(stove_type)

        cooking_colors = {"start": "turquoise",
                          "peak": 'red',
                          "end": "black"}
        fig = go.Figure()

        fig.update_yaxes(title_text="Temp")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text="Household: " + hh_id + " " + stove + " Stove Temperature")

        for s in stove_type:
            fig.add_trace(go.Scatter(
                x=self.df_stoves['timestamp'],
                y=self.df_stoves[s].values,
                mode='lines',
                marker=dict(
                        color=colors[s],
                        size=5),
                name=s.split(' ')[0],
                legendgroup= s
            ))

        if cooking_events:
            events = self.cooking_events(stove)

            for s in stove_type:
                peak = []
                start = []
                end = []
                for point in events[s]:
                    peak.append(point[0])
                    start.append(point[1])
                    end.append(point[2])

                fig.add_trace(
                                go.Scatter(x=self.df_stoves['timestamp'][peak],
                                           y=self.df_stoves[s][peak],
                                           mode='markers',
                                           marker=dict(
                                                    color=cooking_colors['peak'],
                                                    size=5),
                                           name=s + ' Cooking Events',
                                           legendgroup=s

                                           )
                            )
                fig.add_trace(
                                go.Scatter(x=self.df_stoves['timestamp'][start],
                                           y=self.df_stoves[s][start],
                                           mode='markers',
                                           marker=dict(
                                                    color=cooking_colors['start'],
                                                    size=10,
                                                    symbol='triangle-right'),
                                           name=s + ' Cooking start',
                                           legendgroup=s
                                           )
                            )
                fig.add_trace(
                                go.Scatter(x=self.df_stoves['timestamp'][end],
                                           y=self.df_stoves[s][end],
                                           mode='markers',
                                           marker=dict(
                                                    color=cooking_colors['end'],
                                                    size=10,
                                                    symbol='triangle-left'),
                                           name=s + ' Cooking end',
                                           legendgroup=s
                                           )
                            )

        return fig.show()

    def plot_fuel(self, fuel="All Fuels", fuel_usage=False):
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

        # fuel_type = self.check_fuel_type(fuel)
        fuel_type = self._check_item(fuel)

        fig = go.Figure()

        colors = self._color_assignment(fuel_type)

        fig.update_yaxes(title_text="Weight")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text="Household: " + hh_id + " " + fuel + " Weight Readings")

        for f in fuel_type:
            fig.add_trace(
                go.Scatter(
                    x=self.df_stoves['timestamp'],
                    y=self.df_stoves[f].values,
                    mode='lines',
                    marker=dict(
                                color=colors[f],
                                size=5
                                ),
                    name=f.split(' ')[0],
                    legendgroup=f
                ))

        if fuel_usage:
            self.fuel_usage(fuel=fuel_type)
            changes = self.weight_changes

            for f in fuel_type:
                fig.add_trace(
                    go.Scatter(x=self.df_stoves['timestamp'][changes[f]],
                               y=self.df_stoves[f][changes[f]],
                               mode='markers',
                               marker=dict(
                                color='red',
                                size=5
                                ),
                               name=f + ' Weight Change',
                               legendgroup=f
                               )
                )
        return fig.show()
    
    def plot_usage(self, stove, fuel):
        '''This function is still being worked on. Not fully functional!'''
    
        stove_type = self.check_stove_type(stove)
        fuel_type = self.check_fuel_type(fuel)
    
        fig = make_subplots(specs=[[{"secondary_y": True}]])
    
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text="Household: " + hh_id )
    
        colors = {'telia': 'blue',
                        'malgchch': 'red',
                        '3stone': 'green',
                        'om30': 'lavender',
                        'firewood': 'magenta',
                        'charcoal': 'black',
                        'lpg': 'pink'
        }
    
        for s in stove_type:
            fig.add_trace(
                go.Scatter(x=self.df_stoves['timestamp'],
                           y=self.df_stoves[s].values,
                            mode='lines',
                            marker=dict(
                                color=colors[s],
                                size=5),
                            name=s.split(' ')[0]),
                            secondary_y=False,
                    )
    
        for f in fuel_type:
            fig.add_trace(
                    go.Scatter(
                        x=self.df_stoves['timestamp'],
                        y=self.df_stoves[f].values,
                        mode='lines',
                        marker=dict(
                                color=colors[f],
                                size=5
                                ),
                        name=f.split(' ')[0]),
                        secondary_y=True,
                    )
    
        # Set y-axes titles
        fig.update_yaxes(title_text="<b>primary</b> Temperature", secondary_y=False)
        fig.update_yaxes(title_text="<b>secondary</b> Weight", secondary_y=True)

        return fig.show()


if __name__ == "__main__":
    from olivier_file_convert import reformat_olivier_files as reformat

    # filepaths = ['HH_38_2018-08-26_15-01-40_processed_v3.csv',
    #          'HH_44_2018-08-17_13-49-22_processed_v2.csv',
    #          'HH_141_2018-08-17_17-50-31_processed_v2.csv',
    #          'HH_318_2018-08-25_18-35-07_processed_v2.csv',
    #          'HH_319_2018-08-25_19-27-32_processed_v2.csv',
    #          'HH_326_2018-08-25_17-52-16_processed_v2.csv',
    #          'HH_345_2018-08-25_15-52-57_processed_v2.csv',
    #          'HH_371_2018-08-17_15-31-52_processed_v2.csv'
    #          ]
    #
    # for file in filepaths:
    #     df, stoves, fuels, hh_id = reformat('./data_files/' + file)
    #     x = Household(df, stoves, fuels, hh_id)
    #     print(file, '\n',
    #         # x.check_stove_type(),
    #         # x.check_fuel_type('lpg')
    #         # x.cooking_events(),
    #         # x.fuel_usage()
    #         #   , '\n',
    #         # x.cooking_duration(),
    #         # x.df_stoves
    #         # x.study_duration.total_seconds()/86400
    #     )
    #     x.plot_fuel()
    #     x.plot_stove()

    df, stoves, fuels, hh_id = reformat('./data_files/HH_319_2018-08-25_19-27-32_processed_v2.csv')
    x = Household(df, stoves, fuels, hh_id, time_between_events=30, weight_threshold=0.05)
    # print(x._daily_cooking_time(events))
    # print(x.cooking_duration())
    x.plot_fuel(fuel_usage=True)
    # x.plot_stove(cooking_events=True)
    # # x.plot_usage()
    # print(x.color_assignment(x.stoves))

