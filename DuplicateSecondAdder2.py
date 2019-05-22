# INPUT VARIABLES----------------------------------------------------------------------------------------
#region
# Directory folder of the csv files you want to process
Input_path = 'C:/FILES/Hansen-Data-Qualified8.csv'
# Can change to xlsx if needed, other changes will be nessesary to code

# Csv files seperator for input and output files..generally (,) or (|)
Delimiter = ','

# Output file path of data with intersection Removed
Output_path = 'C:/FILES/data_Output.csv'

# The names of the columns that you want to compare,
# ...if there are duplicates then their times will be edited
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
print('--------------LOAD FILE----------------------')
print('Reading Dataframe...')
df_file = pd.read_csv(Input_path, engine = 'python', sep = Delimiter, dtype=object)
print('Created Dataframe.')
print('Shape:')
print(df_file.shape[0])
# Delete Rows with everything missing in the row
df_file.dropna(axis='index', how='all', inplace=True)
print('Removed any blank rows.')
print('Shape:')
print(df_file.shape[0])
print('--------------END LOAD FILE----------------------')
#endregion


# GET BOOLEANS FOR DUPLICATES
#region
print('-----------------FINDING DUPLICATES-----------------------')
# Get Booleans
Bools_Duplicates  = df_file.duplicated(subset=Lst_Columns, keep=False)
# Create Dataframe of only Duplicates including the first one
df_Dups_Only = df_file[Bools_Duplicates]
df_Dups_Only.reset_index(inplace=True, drop=True)
print('Shape of Duplicates Dataframe:')
print(df_Dups_Only.shape)
# Remove duplicates from Original Dataframe
df_file.drop_duplicates(subset=Lst_Columns, keep=False, inplace=True)
df_file.reset_index(inplace=True, drop=True)
print('Shape of Original Dataframe with Dups removed:')
print(df_file.shape)
print('----------------------------------------------------------')
#endregion



# CREATE LIST OF KEYS THAT ARE DUPLICATES
#region
print('-------------CREATING KEYS----------------------------------')
# Create List of Keys
Lst_Row_Key = []
print('Creating Keys to compare...')
for index, row in df_Dups_Only.iterrows():
    Str_Row = str('')
    for item in Lst_Columns:
        Str_Row = Str_Row + row[item]
    Lst_Row_Key.append(Str_Row)
print('Created list of Keys')
print('Example Row Key from first Row:', Lst_Row_Key[0])


# Create Array of Rows from List of Rows
print('Creating Array of keys from list...')
Array_Raw_Items_Results = np.array(Lst_Row_Key)
print('Array creation complete.')

# Create a dictionary of Row Strings to number of Duplicates
print('Creating Dictionary of KEYS:COUNTS...')
unique, counts = np.unique(Array_Raw_Items_Results, return_counts=True)
Dict_Unique_Counts = dict(zip(unique, counts))
print('Dictionary created.')

#Create a list of keys for Duplicates only
print('creating a dictionary of duplicates only...')
Lst_Duplicate_Keys = ([key for key, val in Dict_Unique_Counts.items() if val > 1])
print('Finished creating duplicate dictionary.')
#endregion


# EDIT THE DATA
# For each key find the indexes where they exist
# and then edit the duplicates by adding 1 second (leaving the first one)
# Note: assuming date time ends with last two characters representing the seconds
print('Editing Data in dataframe...')
print('----------------INDEXES OF DUPS -----------------------------')
#region
Lst_Row_Index_Duplicates = []
for key in Lst_Duplicate_Keys:
    # Get the row index's of the duplicate Key
    Lst_Indexes = [i for i, j in enumerate(Lst_Row_Key) if j == key]
    print('----------------------------------------------------------')
    print('Duplicates at indexes:')
    print(Lst_Indexes)
    
    # Append the row index's to a list
    Lst_Row_Index_Duplicates.extend(Lst_Indexes)

    # Remove Fist Duplicate from List because we let the first one load and edit
    # ...the rest by adding a second to the time
    Lst_Indexes.pop(0)

    #Edit the rows in place of the Rows in Lst_Indexes
    counter = int(1)
    for indexval in Lst_Indexes:
        cellval = str(df_Dups_Only.loc[indexval, DTime])

        # Save the last two digits at the end of the cell as an integer
        second = cellval[-2:]
        
        second = int(second)
        if second > 58:
            print('-------------------------------------------------------------')
            print('ERROR - Input second of 59!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('OUTPUT DATA WILL HAVE A SECOND OF > 60')
            print('This is the key with the issue:')
            print(key)
            print('-------------------------------------------------------------')
        second = second + counter
        
        second = str(second)

        if len(second) < 2:
            second = '0' + second
        
        # Change the value of the last two characters in the cell
        newcellval = cellval[:-2] + second
        print(newcellval)
        df_Dups_Only.loc[indexval, DTime] = newcellval
        counter += 1
        
print('Finished editing data in Duplicates Only dataframe.')
print('-------------------------------------------------------------')
#endregion

# Concatenate (join) the Duplicates Only Dataframe with the Non Dups Dataframe
print('Joining Dataframes')
df_file = pd.concat([df_file, df_Dups_Only], ignore_index=True)
print('Shape of output DataFrame:')
print(df_file.shape)

print('Creating the csv file...')
print(Output_path)
# Create Output file for data with only intersection
df_file.to_csv(path_or_buf=Output_path, sep=Delimiter, index=False)
print('File created.')
print('-------END-------------')
