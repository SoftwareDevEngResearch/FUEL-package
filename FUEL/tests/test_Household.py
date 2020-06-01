from ..household import Household
from ..olivier_file_convert import reformat_olivier_files as reformat
from scipy.signal import find_peaks

file_paths = [
    'FUEL/data_files/test_datetime.csv',
]
df, stoves, fuels, hh_id = reformat('FUEL/data_files/test_datetime.csv')
x = Household(df, stoves, fuels, hh_id)


def test_household_study_duration():
    '''Testing the duration of a study is being calculated properly in init function.'''

    assert x.study_duration.days > 0


def test_check_stove_type_1():
    '''Testing that the check stoves function returns the same stoves as the input stoves'''

    for s in x.check_stove_type():
        assert s in stoves


def test_check_stove_type_2():
    '''Testing that the check stoves function returns stoves that are in the dataframe'''

    for s in x.check_stove_type():
        assert s in df.columns


def test_check_fuel_type_1():
    '''Testing that the check fuels function returns the same fuels as the input fuels'''

    for f in x.check_fuel_type():
        assert f in fuels


def test_check_fuel_type_2():
    '''Testing that the check fuels function returns fuels that are in the dataframe'''

    for f in x.check_fuel_type():
        assert f in df.columns


def test_find_weight_changes():
    """Test the _find_significant_weight_changes actually records weights that are greater than the threshold"""

    for f in fuels:
        weight_changes = x._find_weight_changes(f)
        weight = x.df_stoves[f][0]
        for i in (weight_changes[1:]):
            new_weight = x.df_stoves[f][i]
            if i == weight_changes[-1]:
                assert new_weight < weight
                break

            diff = abs(new_weight-weight)
            assert diff >= x.weight_threshold
            weight = new_weight


def test_daily_fuel_use_size():
    '''Testing that the function returns data for every day of study'''

    for f in fuels:
        weights_changes = x._find_weight_changes(f)
        daily_use = x._daily_fuel_use(f, weights_changes)

        assert len(daily_use) == x.study_days + 1


def test_daily_fuel_use_amounts():
    '''Testing that the total usage is equal to the daily usage'''
    for f in fuels:
        weights_changes = x._find_weight_changes(f)
        daily_use = x._daily_fuel_use(f, weights_changes)

        total_usage = 0
        for i in range(x.study_days):
            total_usage += daily_use[i+1]

        assert daily_use[0] == total_usage


def test_fuel_usage_fuels():
    '''Testing that the fuel_usage function returns a dataframe with the appropriate fuels'''

    for f in fuels:
        assert f in x.fuel_usage().columns


def test_fuel_usage_days():
    '''Testing that the fuel_usage function returns a dataframe with the appropriate days'''

    assert len(x.fuel_usage().index) == x.study_days+1


def test_cooking_events():
    '''Testing that the start of one cooking event is not identified as before the end of the previous'''

    stove_events = x.cooking_events()
    for s in stove_events:
        for i, event in enumerate(stove_events[s][1:]):
            previous_end = stove_events[s][i][2]
            current_start = event[1]
            assert current_start > previous_end


def test_daily_cooking_time_size():
    '''Testing that the function returns data for every day of study'''

    for s in stoves:
        stove_events = x.cooking_events(s)
        daily_use = x._daily_cooking_time(stove_events[s])

        assert len(daily_use) == x.study_days + 1


def test_daily_cooking_time_amounts():
    '''Testing that the total usage is equal to the daily usage'''

    for s in stoves:
        stove_events = x.cooking_events(s)
        daily_use = x._daily_cooking_time(stove_events[s])

        total_usage = 0
        for i in range(x.study_days):
            total_usage += daily_use[i+1]

        assert daily_use[0] == total_usage


def test_cooking_duration_days():
    '''Testing that the cooking_duration function returns a dataframe with the appropriate days'''

    assert len(x.cooking_duration().index) == x.study_days+1


def test_cooking_duration_stoves():
    '''Testing that the cooking_duration function returns a dataframe with the appropriate stoves'''

    for s in stoves:
        assert s in x.cooking_duration().columns
