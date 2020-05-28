from ..household import Household
from ..olivier_file_convert import reformat_olivier_files
from scipy.signal import find_peaks

file_paths = [
    'FUEL/data_files/test_datetime.csv',
]


def test_household_study_duration():
    '''Testing the duration of a study is being calculated properly in init function.'''
    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)
    assert x.study_duration.days > 0


def test_check_stove_type_1():
    '''Testing that the check stoves function returns the same stoves as the input stoves'''
    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)
    for s in x.check_stove_type():
        assert s in stoves


def test_check_stove_type_2():
    '''Testing that the check stoves function returns stoves that are in the dataframe'''
    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)
    for s in x.check_stove_type():
        assert s in df.columns


def test_check_fuel_type_1():
    '''Testing that the check fuels function returns the same fuels as the input fuels'''
    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)
    for f in x.check_fuel_type():
        assert f in fuels


def test_check_fuel_type_2():
    '''Testing that the check fuels function returns fuels that are in the dataframe'''
    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)
    for f in x.check_fuel_type():
        assert f in df.columns


def test_cooking_events():
    '''Testing that the self.cooking_events has the same number of cooking events as is reported in number of cooking
    events.'''

    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)
    number_of_events = x.cooking_events()
    for s in number_of_events:
        assert len(x.cook_events[s]) == number_of_events[s]


def test_find_significant_weight_changes():
    """Test the _find_significant_weight_changes actually records weights that are greater than the threshold"""

    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)

    for f in fuels:
        peaks = find_peaks(x.df_stoves[f].values, height=1, distance=1)[0]
        weights_idx = x._find_significant_weight_changes(f, peaks)
        weight = x.df_stoves[f][weights_idx[0]]

        for i in weights_idx[1:]:
            new_weight = x.df_stoves[f][i]
            if i == weights_idx[-1]:
                assert new_weight < weight
                break

            diff = abs(new_weight-weight)
            assert diff >= x.weight_threshold
            weight = new_weight


def test_daily_fuel_use():
    '''Testing that the function returns data for every day of study'''

    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)

    for f in fuels:
        peaks = find_peaks(x.df_stoves[f].values, height=1, distance=1)[0]
        weights_changes = x._find_significant_weight_changes(f, peaks)
        daily_use = x._daily_fuel_use(f, weights_changes)

        assert len(daily_use) == x.study_duration.days


def test_fuel_usage_fuels():
    '''Testing that the fuel_usage function returns a dataframe with the appropriate fuels'''
    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)

    for f in fuels:
        assert f in x.fuel_usage().columns


def test_fuel_usage_days():
    '''Testing that the fuel_usage function returns a dataframe with the appropriate days'''
    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)

    assert len(x.fuel_usage().index) == x.study_duration.days


def test_fuel_usage_values():
    '''Testing that the fuel_usage function returns a dataframe with appropriate values'''

    df, stoves, fuels = reformat_olivier_files('FUEL/data_files/test_1.csv')
    x = Household(df, stoves, fuels)
    fuel_usage = x.fuel_usage()

    for f in fuels:
        fuel_info = x.df_stoves[f]
        peaks = find_peaks(fuel_info.values, height=1, distance=1)[0]
        weights_changes = x._find_significant_weight_changes(f, peaks)
        total_fuel_use = fuel_info[weights_changes[0]] - fuel_info[weights_changes[-1]]

        assert total_fuel_use == sum(fuel_usage[f])













