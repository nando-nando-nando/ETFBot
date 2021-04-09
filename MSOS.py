import csv
import datetime
import pprint
import re
import traceback
import logging
# My modules
import modules.settings
import modules.logs

# Log config
logger = logging.getLogger(__name__)


pp = pprint.PrettyPrinter(indent=4)

# Variables
insheet_date_format = "%m/%d/%Y"
oldsheet_date_format = insheet_date_format
oldsheetDateRegex = r'\d{1,2}\/\d{1,2}\/\d{4}'
today = datetime.datetime.now().strftime(modules.settings.common_date_format)
yesterday = (datetime.datetime.now() - datetime.timedelta(3)).strftime(modules.settings.common_date_format)
holdingsRoot = "holdings/msos"
fileLocTemp = f"{holdingsRoot}/{today}.csv"
fileLocNew = f"{holdingsRoot}/{today}.xlsx"
fileLocOld = f"{holdingsRoot}/{yesterday}.xlsx"
imgFileLocNew = f"{holdingsRoot}/imgs/AdvisorShares_MSOS_Holdings_{today}.png"
url = "https://advisorshares.com/wp-content/uploads/csv/holdings/AdvisorShares_MSOS_Holdings_File.csv"
# header = f'Hey #MSOGang, the latest @AdvisorShares $MSOS holdings are out🌿🇺🇸\n'
header = f'🌿@AdvisorShares $MSOS holdings are out\n#MSOGang 🇺🇸\n'
# header = f'🔥 Hey #MSOGang, @AdvisorShares $MSOS is a big mover today 🔥🇺🇸\n'
TickerColumn = 'C'
SharesColumn = 'F'
rowStart = 1
rowModifier = 0

# Return the date and important rows from the passed worksheet 
def date_and_rows(sheet, header):
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
            header += f'{date}' #Add the sheet's date to the tweet header
            return sheet, date, header
    except Exception as e:
        logger.critical("ERROR: Couldn't collect the date and rows from the latest MSOS holdings csv.")
        logger.critical(e)
        logger.critical(e.__traceback__)
        logging.shutdown()
        exit()
