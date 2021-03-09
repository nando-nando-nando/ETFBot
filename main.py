import datetime
import openpyxl
import pprint
import os
import getopt
import sys
import traceback
import importlib
# My modules
import modules.filehandler
import modules.processor
import modules.twitter

# Get commandline arguments
try:
    options, remainder = getopt.getopt(sys.argv[1:],'e:i')
except getopt.GetoptError as e:
      print ("ERROR:", e.msg)
      print ('\nUsage: main.py [-e <ETF Ticker>] [-i]')
      print ('-e: specific ETF ticker symbol')
      print ('-i: non-interactive run (tweets without prompt)')
      sys.exit(2)

nonInteractive = False
chosenEtf = None
for opt, arg in options:
    if opt in '-e' and not arg.isspace(): # Run the passed ETF
        print('Chosen ETF: ', arg)
        chosenEtf = arg
    elif opt in '-i': # Run in non-interactive mode
        nonInteractive = True

if chosenEtf is None:
    # TODO: add multi-etf logic here
    print("You need to select an ETF for now")
    exit()
else:
    etf=importlib.import_module(chosenEtf) #This loads the etf-specific module and runs any code not in a function

## Load variables from the ETF module
# Dates
oldsheet_date_format = etf.oldsheet_date_format #Takes a little work to figure out, but it's the date format pulled in from previous sheets. This differs from new sheets sometimes due to format changes. 
oldsheetDateRegex = etf.oldsheetDateRegex       #Regex form of the above format
today = etf.today                               #Follows the settings.common_date_format
yesterday = etf.yesterday                       #Follows the settings.common_date_format
# File paths
holdingsRoot = etf.holdingsRoot                 #Root path for the holdings sheet files
fileLocTemp = etf.fileLocTemp                   #.csv file path for the new sheet
fileLocNew = etf.fileLocNew                     #.xlsx file path for the new sheet
fileLocOld = etf.fileLocOld                     #.xlsx file path for the old sheet
imgFileLocNew = etf.imgFileLocNew               #.png file path for the new sheet screenshot
url = etf.url                                   #URL for new holdings file, preferrably .csv
# Tweet stuff
header = etf.header                             #Static tweet message
# Pair separation stuff
TickerColumn = etf.TickerColumn                 #Excel column index for the ticker symbols
SharesColumn = etf.SharesColumn                 #Excel column index for the shares held
rowStart = etf.rowStart                         #First row to start looking for holdings info
rowModifier = etf.rowModifier                   #Hard to explain, tweaks the shares held row offset when storing in newPairs

trackedEtfCount = 4                             #Update by hand for now

# Run common logic and ETF-specific functions
try:
    pp = pprint.PrettyPrinter(indent=4)    

    # Auth with Twitter
    api = modules.twitter.auth()
    pp.pprint("Logged in as " + api.me()._json['name'])

    # Download the latest CSV
    modules.filehandler.collectcsv(fileLocTemp, url)

    wbNew = openpyxl.Workbook()
    sheetNew = wbNew.active
    date = ''

    # Collect the date and holdings rows from the CSV
    sheetNew, date = etf.date_and_rows(sheetNew)

    # Get the previous day's sheet, taking weekends/holidays into account
    wbOld, dateOld = modules.filehandler.previous_day(oldsheet_date_format, oldsheetDateRegex, holdingsRoot, datetime.datetime.strptime(today, modules.settings.common_date_format), 5)
    sheetOld = wbOld.active

    # If the dates on both the latest and last sheet are the same, assume no updates from the fund and exit
    if date == dateOld:
        if os.path.exists(fileLocTemp):
            os.remove(fileLocTemp)
        print(f"\n\nThe latest sheet has the same date ({date}) as the last ({dateOld}), doing nothing for now..")
        exit()

    # Resize new sheet columns and save it
    sheetNew = modules.filehandler.resize_columns(sheetNew)
    wbNew.save(fileLocNew)
    os.remove(fileLocTemp)  

    # Convert Excel sheet to img for tweet attachment
    modules.filehandler.excel_screenshot(fileLocNew, imgFileLocNew)
    
    # Setup dictionaries with old and new sets of ticker/share# pairs
    newPairs, oldPairs = modules.processor.pair_separation(sheetNew, sheetOld, TickerColumn, SharesColumn, rowStart, rowModifier)

    #Separate out newly opened, closed, and updated positions
    diffList, openedList, closedList = modules.processor.position_changes(newPairs, oldPairs)

    tweet = ['']
    lastPage = 0
    if ( not bool(diffList) 
            and not bool(openedList) 
            and not bool(closedList) ):    
        tweet = [f'{header}No changes today!']
        print(f"TWEET: There was no difference in the holdings for {today} and {yesterday}. \nSending the 'no changes' tweet.")                
    else:
        # Build up the tweet message 
        tweet, lastPage = modules.processor.tweet_builder(diffList, openedList, closedList, header)

    # Add a page number if there are more than one pages (280 chars max per tweet)
    tweet = modules.processor.tweet_paginator(lastPage, tweet)    

    # Check for duplicate tweets
    modules.twitter.dupe_check(api, trackedEtfCount*2, tweet[0])

except Exception as e:
    print("ERROR: Something went wrong before tweeting, closing...")
    print(e)
    traceback.print_exc()
    exit()

if modules.processor.query_yes_no("Ready to tweet?"):
    modules.twitter.pic_and_tweet(api, imgFileLocNew, tweet)
    print("TWEET: Holdings tweet sent. Make sure you commit the new files!")
else:
    print("No tweet sent. Closing...")