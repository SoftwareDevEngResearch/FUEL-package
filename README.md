
# FUEL 

During an improved cookstove project if a FUEL sensor is used this tool may be used to vizualize and analyze the data produced by a households cookstove temperature sensor and the weight change information produced by the FUEL sensor. 


## Contained in this Package 

**example datafiles** : These are example files that should be used to test the functionality of the tool as well as examples of what data might look like. 

**example_file_convert.py** : This file was created specificly to convert the example datafiles into the appropriate format for analysis. If your datafiles do not match those of the provided datafiles a new file should be created to prodcue the same outputs. 

**household.py** : This file contains the actual vizualization and analysis tools which are contained within the Household class. 

**tests** : This folder contains a **test_household.py** file as well as an __init__.py file which will be used to test the functionality of the Household class inside **household.py** 

## Getting Started

It is important that before one inputs data into the main file that it is in the correct format. This package contains a eight example data files and a sample data cleaning file (**example_file_convert.py**) which produces data in the correct format for the **household.py** file. If your data does not match the format of the example file you must first reformat your data before using this tool. 

## Correct Data Input Format

* **Dataframe**: Includes columns with the following information (all column names should be lower case) 
  - timestamp : This column should include all timestamp data in datetime format 
  - stoves : Each stove in the household should have its own column with the name being only the name of the stove. The data should be in degrees that are represented as floating numbers. 
  - fuels : Each fuel in the household should have its own column with the name being only the name of the fuel. The data should be in kilograms that are represented as floating numbers. 
* **Stoves** : A list of all stoves in the household, each of which should be a string. These names should match the names of the stoves in the dataframe columns exactly. 
* **Fuels** : A list of all fuels in the household, each of which should be a string. These names should match the names of the fuels in the dataframe columns exactly. 
* **Household ID** : Some sort of unique houehold identification should be assigned and should be input as a string. 

### Packages Needed to Run Files 

For **example_file_convert.py** 
* pandas 
* numpy 

For **household.py** 
* pandas 
* plotly
* scipy 

### Installing
To install the package you can either 
* Clone a local copy of this package directly from the github page 
```
https://github.com/HeatherMM1321/FUEL-package
```
* Use pip install with the following command 
```
pip install -i https://test.pypi.org/simple/ FUEL-millerh
```
Once the package is installed along with all dependencies files, you can obtain stove and fuel usage metrics as well as view interactive plots by using the Household class in household. See example below for more detail. 

### Example 
To run this example using the example data files provided you will first need to input the datafile in to the **example_file_convert.reformat_example_file()** function as shown below. For this example I will be using the data file labeld as **HH_319_2018-08-25_19-27-32_processed_v2.csv** (it should be noted that the example_file_convert will only work with data that is formated like the example files. If you wish to use other datafiles you will need to reformat your data to match the outputs that this file produces). 

```
from FUEL.example_file_convert import reformat_example_file as reformat 

df, stoves, fuels, hh_id = reformat('HH_319_2018-08-25_19-27-32_processed_v2.csv') 
```
This will produce a dataframe,  ![alt text](https://github.com/HeatherMM1321/FUEL-package/blob/master/example_outputs/df_output.PNG)
a list of all of the stoves in the dataset, 
```
['om30', '3stone', 'telia']
```
a list of all of the fuels in the dataset, 
```
['lpg', 'charcoal', 'firewood'] 
```
and finally the household identification. 

```
319
```
This is the data you will need as inputs for the **Household** tool. 

Next you will need to import the **household.Household** function 

```
from FUEL.household import Household 

Household(df, stove, fuels, hh_id) 
```
This will produce a dataframe containing usage information for each stove and fuel in the household. Where total is the total usage during the entire study and each row corresponds to a single 24 hour period in the study.

![alt text](https://github.com/HeatherMM1321/FUEL-package/blob/master/example_outputs/dataframe.PNG) 

An interactive html based plot for both fuel and stove usage will also be produced. 
![alt text](https://github.com/HeatherMM1321/FUEL-package/blob/master/example_outputs/fuel.PNG) 
![alt text](https://github.com/HeatherMM1321/FUEL-package/blob/master/example_outputs/stove_full.PNG) 

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```



## Authors

* **Heather Miller** 


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
