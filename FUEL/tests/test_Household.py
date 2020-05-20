from fuel import household


def test_reformat_olivier_files():
    '''make sure that the output stoves and fuels are in the dataframe.'''

    df_columns = df.columns

    for s in stoves:
        assert s in df_columns

    for f in fuels:
        assert f in df_columns


def test_Household_studyduration():
    '''Testing the duration of a study is being calculated properly in init function.'''

    assert x.study_duration.days > 0


def test_stove_check(): 
    '''Testing that function works for an individual stove input and all stove inputs at once.'''

    # check_stove_type() output is a list so we must pull the first value to check it
    for s in x.stoves:
        assert x.check_stove_type(s)[0] in x.stoves

    assert x.stoves == x.check_stove_type()


def test_fuel_check():
    '''Testing that function works for an individual fuel input and all fuel inputs at once.'''

    # check_fuel_type() output is a list so we must pull the first value to check it
    for f in x.fuels:

        assert x.check_fuel_type(f)[0] in x.fuels

    assert x.fuels == x.check_fuel_type()


def test_cooking_events():
    '''Testing that the number of cooking events produced matches the length of the list containing all cooking event
    locations.'''

    number_events = x.cooking_events()
    event_loaction = x.cook_events

    for i, stove in enumerate(number_events):
        assert number_events[stove] == len(event_loaction[stove])


def test_fuel_usage():
    '''Test functions in fuel usage'''
    df_fuel_usage = x.fuel_usage()

    def test_fuels():
        '''Testing that all fuels in dataframe are shown.'''

        for f in x.fuels:
            assert f in df_fuel_usage.index

    def test_days():
        '''Test that the correct number of days are in the fuel usage data frame'''

        assert x.study_duration.days == len(df_fuel_usage.columns)

    def test_content():
        '''Test that all values of the data frame are floats'''

        for col in df_fuel_usage.columns:
            assert df_fuel_usage[col].dtype == 'float64'

    test_fuels()
    test_days()
    test_content()


def test_cooking_duration():
    '''Test all functions in cooking duration.'''
    df_cooking_time = x.cooking_duration()

    def test_stoves():
        '''Testing that all stoves in dataframe are shown.'''

        for s in x.stoves:
            assert s in df_cooking_time.index

    def test_days():
        '''Test that the correct number of days are in the cooking duration data frame'''

        assert x.study_duration.days == len(df_cooking_time.columns)

    def test_content():
        '''Test that all values of the data frame are floats'''

        for col in df_cooking_time.columns:
            assert df_cooking_time[col].dtype == 'float64'

    test_stoves()
    test_days()
    test_content()

    
files = open('../data_files/test_file_paths.txt', 'r')
contents = files.read().split(',')
files.close()


for path in contents:
    df, stoves, fuels = household.reformat_olivier_files(path)
    x = household.Household(df, stoves, fuels)
    test_reformat_olivier_files()
    test_Household_studyduration()
    test_stove_check()
    test_fuel_check()
    test_cooking_events()
    test_fuel_usage()
    test_cooking_duration()




