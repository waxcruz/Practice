'''
Created on Aug 29, 2019

@author: waxcruz
'''

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import xlrd
from pathlib  import Path
from tokenize import String
import datetime
import csv
from iso3166 import countries
import sys
from matplotlib.backend_bases import _default_filetypes
import os
from docutils.utils.math.math2html import Newline
from pandas.core.config_init import colheader_justify_doc
from dill.dill import check
from math import isnan
from numpy.f2py.common_rules import findcommonblocks
from io import StringIO
import csv

def processAHNowData():
    # read AHNow's Firebase Analytics data, AHNowData parameter for AHNow events.
    # File must be in the home directory in a folder named AHNow
    filenameAHNowData = home + "/AHNow/ahnow.csv"
    eventsFile = open(filenameAHNowData, 'r', encoding='utf8')
    events = []
    counts = []
    # Position to Users
    for line in eventsFile:
        if 'Nth day,Users\n' == line:
            break
    # read AHNowData users by day 
    for line in eventsFile:
        if '\n' == line[-1]:
            line = line[:-1]
            if len(line) == 0:
                break        
        parts = line.split(',')
        counts.append(parts[1])        
    #Position to AHNowData
    for line in eventsFile:
        if '# AHNowData #\n' == line:
            break
    # skip over event counts
    for line in eventsFile:
        if '\n' == line[-1]:
            line = line[:-1]
            if len(line) == 0:
                break        
    # read event data   
    for line in eventsFile:
        # strip new lines from data
        if '\n' == line[-1]:
            line = line[:-1]
            if len(line) == 0:
                break
        stringFile = StringIO(line)
        stringReader = csv.reader(stringFile, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for token in stringReader:
            events.append(token)
    # remove header for events
    events.pop(0)
    return [counts, events]

def buildExcelframes(counts, events):
    print(counts, events)
    
    

def createAHNowWorkbook(dataForAHNow):

    #===========================================================================
    # Creates ahnow.xlsx file
    #===========================================================================
    ahnowReportsFileName = home + "/ahnow/ahnowReports.xlsx"
    ahnowReportsFilePath = Path(ahnowReportsFileName)
    if ahnowReportsFilePath.exists():
        # rename 
        ahnowTime = datetime.datetime.today().strftime("%Y%m%d_%H%M%S%f")
        ahnowReportsFilePath.rename(home+"/ahnow/ahnowReports_" + ahnowTime + ".xlsx")
    # process every child of Firebase's root node
    writer = ExcelWriter(home+'/ahnow/ahnowReports.xlsx')
    for reportIndex in range(len(dataForAHNow)):
        if reportIndex == 0:
            # process counts
            excelRows = []
            counts = dataForAHNow[reportIndex]
            for count in counts:
                countCell = {'Sessions':int(count)}
                excelRows.append(countCell)
            ahNowDataFrame = pd.DataFrame.from_dict(excelRows)
            ahNowDataFrame.to_excel(writer, sheet_name = "Sessions", index=False)            
        else:
            # process events           
            excelRows = []
            events = dataForAHNow[reportIndex]
            excelColHeadings = ['AHNow 1. Category', 'AHNow 2. Action', 'AHNow 3. Label', 'AHNow 4. Value', 'Total Event Count', 'Total Sessions']
            for event in events:
                #process event
                if len(event) != 3:
                    print("Error in event (not 3 tokens: ", event)
                    continue
                ahNowParameter = event[0]
                ahNowEventCount = int(event[1])
                ahNowEventTotalSessions = int(event[2])
                ahData = ahNowParameter.split('|')
                excelRow = {'AHNow 1. Category': '',  'AHNow 2. Action':'', 'AHNow 3. Label' :  '', 'AHNow 4. Value': '', 'Total Event Count' :  '', 'Total Sessions' : ''}
                for parmIndex in range(len(ahData)):
                    excelRow[excelColHeadings[parmIndex]] = ahData[parmIndex]
                excelRow['Total Event Count'] = ahNowEventCount
                excelRow['Total Sessions'] = ahNowEventTotalSessions
                excelRows.append(excelRow)
            ahNowDataFrame = pd.DataFrame.from_dict(excelRows)
            ahNowDataFrame.to_excel(writer, sheet_name = "Events", index=False)            

    writer.close()

# def mapFirebaseFieldsToExcelColumns(nodeName, dataFrame): 
#     # given a Firebase node, map fields to Excel dataFrame with matching names
#     
#     validFirebaseFields = list(colHeaders[nodeName].keys()) # list of Firebase field names
#     mapFirebaseToExcel = {}
#     # get names of columns from the Excel dataFrame
#     fieldPositionInExcel = {}
#     for colIndex in range(len(dataFrame.columns)):
#         if dataFrame.columns[colIndex] in validFirebaseFields:
#             mapFirebaseToExcel[dataFrame.columns[colIndex]] = colIndex
#     # first column 
#     if len(validFirebaseFields) != len(mapFirebaseToExcel):
#         print("Missing Firebase fields for ", nodeName, " in Excel worksheet. Check work and rerun script")
#     return mapFirebaseToExcel


# Setup 
#
# Globals
#

#===============================================================================
# Main 
#===============================================================================
#
#
#

home = str(Path.home())
#
# retrieve AHNowData as counts and events
#
ahnowData = processAHNowData()
colHeaders = {}

# initialize Firebase access
ahnowFileName = home + "/AHNow/ahnow.csv"
ahnowFilePath = Path(ahnowFileName)
if not ahnowFilePath.exists() :
    print("no ahnow.csv file found. Download from Firebase console, events")
else:
    print("opened opened input file, ", ahnowFileName)
    createAHNowWorkbook(ahnowData) # produce reports

print("Finished AHNow backend processing")
