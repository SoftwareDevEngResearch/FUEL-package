from ..household import Household
from ..olivier_file_convert import reformat_olivier_files

file_paths = [
    'FUEL/data_files/test_datetime.csv',
    'FUEL/data_files/test_stoveinfostart.csv'
]

def test_Household_studyduration():
    '''Testing the duration of a study is being calculated properly in init function.'''
    for path in file_paths:
        df, stoves, fuels = reformat_olivier_files(path)
        x = Household(df, stoves, fuels)
        assert x.study_duration.days > 0












