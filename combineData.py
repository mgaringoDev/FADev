#%%
# Cummuliative Sum Play Ground
#%% 
# standard library
import os
from os import listdir
from os.path import isfile, join

# pydata stack
import pandas as pd

#%% Main function of the program
def runningMain():
    #%% Get the directory and retreive only the files
    directoryOfData = os.getcwd();
    directoryOfCSVs = directoryOfData + '\csvData'
    
    onlyfiles = [f for f in listdir(directoryOfCSVs) if isfile(join(directoryOfCSVs, f))]
    
    #%% Read the files and append them into one data frame    
    headerNames = ['Date','Title','Comment','MainCategory','Subcategory','Account','Amount','Balance']
    for csvFileName in onlyfiles:
        fileFullPath = directoryOfCSVs + '\\' + csvFileName
    #    dfList.append(pd.read_csv(fileFullPath))
        try:            
            print('Appended %s to the data frame'%csvFileName)
            df = pd.read_csv(fileFullPath)
            df.columns = headerNames
            allData = allData.append(df,ignore_index=True)
        except:
            print('Could not appended %s to the data frame so creating a new one '%csvFileName)
            df = pd.read_csv(fileFullPath)
            df.columns = headerNames
            allData = df    
            
    #%% Write the combined data frame into a csv file
    allData.to_csv('TogetherProgrammed.csv', sep=',',header=True,cols=headerNames,index=False)
    
#%% Used for excecution of the program in the terminal  
if __name__ == '__main__':
    runningMain()



