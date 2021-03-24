import csv
import datetime
import pprint
import re
import traceback
import logging
# My modules
import modules.settings
import modules.logs

pp = pprint.PrettyPrinter(indent=4)

# Log config
logger = logging.getLogger(__name__)

# Filenames
insheet_date_format = "%m/%d/%Y"
oldsheet_date_format = insheet_date_format
oldsheetDateRegex = r'\d{1,2}\/\d{1,2}\/\d{4}'
today = (datetime.datetime.now()).strftime(modules.settings.common_date_format)
yesterday = (datetime.datetime.now() - datetime.timedelta(1)).strftime(modules.settings.common_date_format)
holdingsRoot = "holdings/mj"
fileLocTemp = f"{holdingsRoot}/{today}.csv"
fileLocNew = f"{holdingsRoot}/{today}.xlsx"
fileLocOld = f"{holdingsRoot}/{yesterday}.xlsx"
imgFileLocNew = f"{holdingsRoot}/imgs/ETFMG_AltHarvest_MJ_Holdings_{today}.png"
url = "https://etfmg.com/holdings/MJ_fund_holdings.csv"
header = f'The latest @ETFMG $MJ holdings are out🌿\n#potstocks\n'
TickerColumn = 'H'
SharesColumn = 'J'
rowStart = 1
rowModifier = 0

#  Return the date and important rows from the passed worksheet 
def date_and_rows(sheet, header):
    try:
        date = None
        with open(fileLocTemp) as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                match = re.search(r'\d{1,2}\/\d{1,2}\/\d{4}', row[0])
                if  date is None and match is not None: #Get the date           
                    print(match.group()) 
                    date = datetime.datetime.strptime(match.group(), insheet_date_format).date().strftime(modules.settings.common_date_format)                    
                # if row[1] == "Account":
                #     sheet.append(row)
                #     pp.pprint(row[2])
                # if row[1] == "CNBS" and "Cash" not in row[2]:
                #     # print(row[2])
                #     sheet.append(row)
                #     pp.pprint(row[2]) 
                if  "Cash" not in row[8] and not row[7].isspace(): #Get the holdings rows
                    # pp.pprint(row[2])                    
                    sheet.append(row)
            header += f'{date}' #Add the sheet's date to the tweet header
            return sheet, date, header
    except Exception as e:
        logger.critical("ERROR: Couldn't collect the date and rows from the latest MJ holdings csv.")
        logger.critical(e)
        logger.critical(e.__traceback__)
        logging.shutdown()
        exit()