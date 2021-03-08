import csv
import datetime
import openpyxl
import pprint
import re
import os
# My modules
import filehandler
import processor
import settings
import twitter
import traceback
import importlib
import getopt
import sys
# Get arguments
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

etf=importlib.import_module(chosenEtf) #This loads the etf-specific module and runs any code not in a function

# Load variables from the ETF module
# Dates
insheet_date_format = etf.insheet_date_format
oldsheet_date_format = etf.oldsheet_date_format
oldsheetDateRegex = etf.oldsheetDateRegex
today = etf.today
yesterday = etf.yesterday
# File paths
holdingsRoot = etf.holdingsRoot
fileLocTemp = etf.fileLocTemp
fileLocNew = etf.fileLocNew
fileLocOld = etf.fileLocOld
imgFileLocNew = etf.imgFileLocNew
url = etf.url
# Tweet stuff
header = etf.header
# Pair separation stuff
TickerColumn = 'C'
SharesColumn = 'F'
rowStart = 1
rowModifier = 0

# Run common logic and ETF-specific functions
try:
    pp = pprint.PrettyPrinter(indent=4)

    

    # Auth with Twitter
    api = twitter.auth()
    pp.pprint("Logged in as " + api.me()._json['name'])

    # Download the latest CSV
    filehandler.collectcsv(fileLocTemp, url)

    wbNew = openpyxl.Workbook()
    sheetNew = wbNew.active
    date = ''

    # Grab the date and important rows. 
    # This is ETF specific
    try:
        with open(fileLocTemp) as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                match = re.search(r'\d{1,2}\/\d{1,2}\/\d{4}', row[0]) 
                if  match is not None: #Get the date           
                    date = datetime.datetime.strptime(match.group(), insheet_date_format).date().strftime(settings.common_date_format)                    
                if  row[2] and not row[2].isspace(): #Get the holdings rows
                    # pp.pprint(row[2])
                    sheetNew.append(row)
    except Exception as e:
        print("ERROR: Couldn't collect the date and rows from the latest holdings csv. ")
        print(e)
        print(e.__traceback__)
        exit()

    # Get the previous day's sheet, taking weekends/holidays into account
    wbOld, dateOld = filehandler.previous_day(oldsheet_date_format, oldsheetDateRegex, holdingsRoot, datetime.datetime.now(), 5)
    sheetOld = wbOld.active

    # If the dates on both the latest and last sheet are the same, assume no updates from the fund and exit
    if date == dateOld:
        if os.path.exists(fileLocTemp):
            os.remove(fileLocTemp)
        print(f"\n\nThe latest sheet has the same date ({date}) as the last ({dateOld}), doing nothing for now..")
        exit()

    # Resize new sheet columns and save it
    sheetNew = filehandler.resize_columns(sheetNew)
    wbNew.save(fileLocNew)
    os.remove(fileLocTemp)  

    # Convert Excel sheet to img for tweet attachment
    import excel2img
    excel2img.export_img(fileLocNew,imgFileLocNew,None, None)

    # Setup dictionaries with old and new sets of ticker/share# pairs
    newPairs, oldPairs = processor.pair_separation(sheetNew, sheetOld, TickerColumn, SharesColumn, rowStart, rowModifier)

    #Separate out newly opened, closed, and updated positions
    diffList, openedList, closedList = processor.position_changes(newPairs, oldPairs)

    tweet = ['']
    lastPage = 0
    if ( not bool(diffList) 
            and not bool(openedList) 
            and not bool(closedList) ):    
        tweet = [f'{header}No changes today!']
        print(f"TWEET: There was no difference in the holdings for {today} and {yesterday}. \nSending the 'no changes' tweet.")        
        # exit()
    else:
        # Build up the tweet message 
        tweet, lastPage = processor.tweet_builder(diffList, openedList, closedList, header)

    # Add a page number if there are more than one pages (280 chars max per tweet)
    tweet = processor.tweet_paginator(lastPage, tweet)    
except Exception as e:
    print("ERROR: Something went wrong before tweeting, closing...")
    print(e)
    traceback.print_exc()
    exit()

if processor.query_yes_no("Ready to tweet?"):
    twitter.pic_and_tweet(api, imgFileLocNew, tweet)
    print("TWEET: Holdings tweet sent.")
else:
    print("No tweet sent. Closing...")


# i=importlib.import_module(chosenEtf) #This runs the etf-specific module
