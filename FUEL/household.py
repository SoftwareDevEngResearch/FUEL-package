import pandas as pd
import numpy as np
import plotly.graph_objects as go

class Household:

    def __init__(self, datafile):
        self.data = pd.read_csv(datafile, header = None)
        #df = self.data
        for (r, name) in enumerate(self.data[0]):
            if name == "Timestamp":
                stove_info_start = r

        df_stoves = self.data.iloc[stove_info_start:, :]
        df_stoves = df_stoves.reset_index(drop=True)
        df_stoves.columns = df_stoves.iloc[0]
        df_stoves = df_stoves[1:]

        df_stoves = df_stoves.apply(lambda x: np.float64(x) if x.name != 'Timestamp' else x)
        df_stoves['Timestamp'] = pd.to_datetime(df_stoves['Timestamp'], format='%m/%d/%Y %H:%M')
        self.df_stoves = df_stoves

    def stove_types(self):
        '''what stove types are captured in data'''

        stove_types = []
        for col in self.df_stoves.columns:
            if "temp" in col.lower():
                stove_name = col.split(' ')[0]
                stove_types.append(stove_name)
        return stove_types

    def fuel_types(self):
        '''what fuel types are captured in data'''

        fuel_types = []
        for col in self.df_stoves.columns:
            if "fuel" in col.lower():
                fuel_name = col.split(' ')[0]
                fuel_types.append(fuel_name)
        return fuel_types

    def plot_stove(self, stove="All"):
        '''plot the data for the stove temperature for all or just one of the stoves'''

        if stove == "All":
            stove_type = self.stove_types()
        else:
            stove_type = [stove]

        fig = go.Figure()

        fig.update_yaxes(title_text="Temp")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text= stove + " Stove Temperature")

        for i, stove in enumerate(stove_type):
            for col in self.df_stoves.columns:
                if "temp" in col.lower() and stove.lower() in col.lower():
                    fig.add_trace(go.Scatter(
                        x=self.df_stoves['Timestamp'],
                        y=self.df_stoves[col].values,
                        mode='lines',
                        name=stove,
                        ))
        return fig.show()

    def plot_fuel(self, fuel="All"):
        '''plot the data for the fuel weights for all or just one of the recorded fuel'''

        if fuel == "All":
            fuel_type = self.fuel_types()
        else:
            fuel_type = [fuel]

        fig = go.Figure()

        fig.update_yaxes(title_text="Weight")
        fig.update_xaxes(title_text="Time")
        fig.update_layout(title_text= fuel + " Weight Readings")

        for i, fuel in enumerate(fuel_type):
            for col in self.df_stoves.columns:
                if "fuel" in col.lower() and fuel.lower() in col.lower():
                    fig.add_trace(go.Scatter(
                        x=self.df_stoves['Timestamp'],
                        y=self.df_stoves[col].values,
                        mode='lines',
                        name=fuel,
                        ))
        return fig.show()

x = Household('./olivier_files/HH_38_2018-08-26_15-01-40_processed_v3.csv')

print(x.stove_types())
x.plot_stove()


if __name__ == "__main__":
   print("yep")

