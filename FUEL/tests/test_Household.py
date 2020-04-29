from household import Household
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# this data contains 3 stoves ['telia', 'OM30', '3Pierres']
# this data set contains 3 fuels [
data = './olivier_files/test_4.csv'

def setUp(data):
    # Expected output of the init function should be a data that has the timestamp formatted as datetime
    # there should be a list of the stoves in the data set
    # there be a list of fuels in the data set


def test_stove_types():
    # Expected output: Should be a list of the names of the stoves in the data set with no additional information


def test_fuel_types():
    # Expected output: Should be a list of the names of the fuels in the data set with no additional information


def test_plot_stove():
    # Expected output: a figure of the temperature data for selected stoves (should not be generated unless followed by
    #.show())

def test_plot_fuels():
    # Expected output: a figure of the weight data for selected fuels (should not be generated unless followed by
    #.show())

def cooking_events():
    # Expected outputs: a dictionary that includes selected stoves and the number of cooking events recorded for each
    # stove.
    # Should test this by creating a data set with a known number of cooking events and ensuring that the correct number
    # is found.

def plot_cooking_events():
    # Expected output: a figure of the temperature data for selected stoves with the cooking events marked
    # (should not be generated unless followed by.show())
