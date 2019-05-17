# INPUT VARIABLES----------------------------------------------------------------------------------------
#region
# Directory folder of the csv files you want to process
Input_path = 'C:/FILES/Hansen-Data-Qualified8.csv'
# Can change to xlsx if needed, other changes will be nessesary to code

# Csv files seperator for input and output files..generally (,) or (|)
Delimiter = ','

# Output file path of data with intersection Removed
Output_path = 'C:/FILES/data_Output.csv'

# The names of the columns that you want to compare, if they are duplicates they will be edited
Lst_Columns = ['DATE-TIME', 'SPOTCODE-E', 'WONO-E']

# The column name you want to add a second to
DTime = 'DATE-TIME'

print('Directories loaded...')
#endregion



# IMPORTING LIBRARIES 
#region
print('Importing Libraries...')
import pandas as pd
import numpy as np
import os
import re
import glob
import csv
import shutil
print('Imported Libraries')
#endregion



# LOAD FILE
#region
print('Reading Dataframe...')
df_file = pd.read_csv(Input_path, engine = 'c', sep = Delimiter, dtype=object)
print('Created Dataframe.')
# Delete Rows with everything missing in the row
df_file = df_file.dropna(axis='index', how='all')
print('Removed any blank rows.')
#endregion



# CREATE LIST OF KEYS THAT ARE DUPLICATES
#region

# Create List of Keys
Lst_Row_Key = []

print('Creating Keys to compare...')
for index, row in df_file.iterrows():
    Str_Row = str('')
    for item in Lst_Columns:
        Str_Row = Str_Row + row[item]
        print(Str_Row)
    Lst_Row_Key.append(Str_Row)
print('Created list of Keys')
print('Example Row Key from firt Row:', Lst_Row_Key[0])

print('Doing Stuff...')
# Create Array of Rows from List of Rows
Array_Raw_Items_Results = np.array(Lst_Row_Key)

# Create a dictionary of Row Strings to number of Duplicates
unique, counts = np.unique(Array_Raw_Items_Results, return_counts=True)
Dict_Unique_Counts = dict(zip(unique, counts))

#Create a list of keys for Duplicates only
Lst_Duplicate_Keys = ([key for key, val in Dict_Unique_Counts.items() if val > 1])
print('Finished doing stuff.')
#endregion



# For each key find the indexes where they exist
# and then edit the duplicates by adding 1 second (leaving the first one)
# Note: assuming date time ends with last two characters representing the seconds
print('Editing Data...')
#region
Lst_Row_Index_Duplicates = []
for key in Lst_Duplicate_Keys:
    # Get the row index's of the duplicate Key
    Lst_Indexes = [i for i, j in enumerate(Lst_Row_Key) if j == key]
    print('Duplicates')
    print(Lst_Indexes)
    
    # Append the row index's to a list
    Lst_Row_Index_Duplicates.extend(Lst_Indexes)

    # Remove Fist Duplicate from List because we let the first one load and edit the rest
    Lst_Indexes.pop(0)

    #Edit the rows in place of the Rows in Lst_Indexes
    counter = int(1)
    for indexval in Lst_Indexes:
        cellval = str(df_file.loc[indexval, DTime])

        # Save the last two digits at the end of the cell as an integer
        second = cellval[-2:]
        
        second = int(second)
        if second > 58:
            print('ERROR - Input second of 59!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('OUTPUT DATA WILL HAVE A SECOND OF > 60')
            print(key)
        second = second + counter
        
        second = str(second)

        if len(second) < 2:
            second = '0' + second
        
        # Change the value of the cell
        newcellval = cellval[:-2] + second
        df_file.loc[indexval, DTime] = newcellval

        counter += 1
print('Finished editing data.')
#endregion

print('Creating the csv file...')
# Create Output file for data with only intersection
df_file.to_csv(path_or_buf=Output_path, sep=Delimiter, index=False)
print('-------END-------------')