import csv
import datetime
import pprint
import re
import logging
# My modules
import modules.settings
import modules.logs

# Log config
logger = logging.getLogger(__name__)

# @retry(stop=stop_after_attempt(4))
pp = pprint.PrettyPrinter(indent=4)

# Variables
insheet_date_format = "%m/%d/%Y"
oldsheet_date_format = insheet_date_format
oldsheetDateRegex = r'\d{2}\/\d{2}\/\d{4}'
today = datetime.datetime.now().strftime(modules.settings.common_date_format)
yesterday = (datetime.datetime.now() - datetime.timedelta(1)).strftime(modules.settings.common_date_format)
holdingsRoot = "holdings/potx"
fileLocTemp = f"{holdingsRoot}/{today}.csv"
fileLocNew = f"{holdingsRoot}/{today}.xlsx"
fileLocOld = f"{holdingsRoot}/{yesterday}.xlsx"
imgFileLocNew = f"{holdingsRoot}/imgs/GlobalX_POTX_Holdings_{today}.png"
url = "https://www.globalxetfs.com/funds/potx/?download_full_holdings=true"
header = f'🌿@GlobalXETFs $POTX holdings are out\n#potstocks 🇨🇦🇬🇧🇺🇸🇦🇺\n'
TickerColumn = 'B'
SharesColumn = 'F'
rowStart = 2
rowModifier = 1

# Return the date and important rows from the passed worksheet 
def date_and_rows(sheet, header):
    try:
        with open(fileLocTemp) as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                # pp.pprint(row[0])
                match = re.search(r'\d{1,2}\/\d{1,2}\/\d{4}', row[0]) 
                if  match is not None: #Get the date           
                    date = datetime.datetime.strptime(match.group(), insheet_date_format).date().strftime(modules.settings.common_date_format)
                if "information" not in row[0] and row[2] != "CASH": #Get the holdings rows
                    sheet.append(row)
            header += f'{date}' #Add the sheet's date to the tweet header
            return sheet, date, header
    except Exception as e:
        logger.critical("ERROR: Couldn't collect the date and rows from the latest holdings csv. ")
        logger.critical(e)
        logger.critical(e.__traceback__)
        logging.shutdown()
        exit()