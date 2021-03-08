import urllib.request
import csv
import openpyxl
import datetime
import re
# My modules
import modules.settings


# Saves the CSV to local storage
# Most ETFs publish their holdings as CSVs
def collectcsv(file_location, url):
    urllib.request.urlretrieve(url, file_location)  # For Python 3

# Returns the workbook for the last day recorded and the date in that book
# today: pass datetime.now()
# search_range: how far into the past to look for a workbook
def previous_day(insheet_date_format_datetime, insheet_date_format_regex, file_root, today, search_range):    
    
    # Finding the last file:
    # Loop 5 days back (compensates for weekends and long holidays)
    for i in range(1, search_range):
        try:
            # For each day, lookg for a date in the first few rows. Otherwise, move on
            prevday = (today - datetime.timedelta(i)).strftime(modules.settings.common_date_format)        
            fileLoc = f"{file_root}/{prevday}.xlsx"        
            wb = openpyxl.load_workbook(fileLoc, data_only=True)
            ws = wb.active
            # Look at the top 4 rows in the first column for the date 
            for row in ws.iter_rows(min_row=1, max_col=1, max_row=4, values_only=True):            
                print(row[0])
                match = re.search(insheet_date_format_regex, str(row[0]))#This row index is ETF-specific, but they all use it so far
                if match is not None:
                    date = datetime.datetime.strptime(match.group(), insheet_date_format_datetime).date().strftime(modules.settings.common_date_format)
                    print(f"Found a previous holdings file: {wb.active}")
                    return wb, date         
        except FileNotFoundError as fe:
            print(f"Expected error: {fe}")
    # If no match 5 days back, throw an error and exit
    raise Exception("No holdings file found within the last 5 days")

# Resizes a worksheet's columns to fit their contents, then returns it
def resize_columns(ws):
    for column_cells in ws.columns: 
        unmerged_cells = list(filter(lambda cell_to_check: cell_to_check.coordinate not in ws.merged_cells, column_cells)) 
        length = max(len(str(cell.value)) for cell in unmerged_cells) 
        ws.column_dimensions[unmerged_cells[0].column_letter].width = length * 1.2
    return ws


