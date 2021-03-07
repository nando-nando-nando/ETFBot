import urllib.request
import csv
import openpyxl
import datetime
import settings
import re

# Saves the CSV to local storage
# Most ETFs publish their holdings as CSVs
def collectcsv(file_location, url):
    urllib.request.urlretrieve(url, file_location)  # For Python 3

# Returns the workbook for the last day recorded
# today: pass datetime.now()
# search_range: how far into the past to look for a workbook
def previous_day(file_root, today, search_range):    
    
    # Finding the last file:
    # Loop 5 days back (compensates for weekends and long holidays)
    for i in range(1, search_range):
        try:
            # For each day, lookg for a date in the first few rows. Otherwise, move on
            prevday = (today - datetime.timedelta(i)).strftime(settings.common_date_format)        
            fileLoc = f"{file_root}/{prevday}.xlsx"        
            wb = openpyxl.load_workbook(fileLoc, data_only=True)
            ws = wb.active
            # Look at the top 4 rows in the first column for the date 
            for row in ws.iter_rows(min_row=1, max_col=1, max_row=4, values_only=True):            
                match = re.search(r'\d{2}\/\d{2}\/\d{4}', row[0]) #TODO: Variablize the match string
                if match is not None:
                    print(f"Found a previous holdings file: {wb.active}")
                    return wb        
        except FileNotFoundError as fe:
            print(f"Expected error: {fe}")
    # If no match 5 days back, throw an error and exit
    raise Exception("No holdings file found within the last 5 days")

        


