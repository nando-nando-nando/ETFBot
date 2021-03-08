import csv
import datetime
import pprint
import re
# My modules
import modules.settings

pp = pprint.PrettyPrinter(indent=4)

# Variables
insheet_date_format = "%m/%d/%Y"
oldsheet_date_format = "%Y-%m-%d"
oldsheetDateRegex = r'\d{4}-\d{1,2}-\d{1,2}'
today = datetime.datetime.now().strftime(modules.settings.common_date_format)
yesterday = (datetime.datetime.now() - datetime.timedelta(3)).strftime(modules.settings.common_date_format)
holdingsRoot = "holdings/yolo"
fileLocTemp = f"{holdingsRoot}/{today}.csv"
fileLocNew = f"{holdingsRoot}/{today}.xlsx"
fileLocOld = f"{holdingsRoot}/{yesterday}.xlsx"
imgFileLocNew = f"{holdingsRoot}/imgs/AdvisorShares_YOLO_Holdings_{today}.png"
url = "https://advisorshares.com/wp-content/uploads/csv/holdings/AdvisorShares_YOLO_Holdings_File.csv"
header = f'The latest @AdvisorShares $YOLO holdings are out🌿🇨🇦\n#potstocks\n{today}\n\n'
TickerColumn = 'C'
SharesColumn = 'F'
rowStart = 1
rowModifier = 0

# Return the date and important rows from the passed worksheet 
def date_and_rows(sheet):
    try:
        with open(fileLocTemp) as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                match = re.search(r'\d{1,2}\/\d{1,2}\/\d{4}', row[0]) 
                if  match is not None: #Get the date           
                    date = datetime.datetime.strptime(match.group(), insheet_date_format).date().strftime(modules.settings.common_date_format)                    
                if  row[2] and not row[2].isspace(): #Get the holdings rows
                    # pp.pprint(row[2])
                    sheet.append(row)
            return sheet, date
    except Exception as e:
        print("ERROR: Couldn't collect the date and rows from the latest holdings csv. ")
        print(e)
        print(e.__traceback__)
        exit()