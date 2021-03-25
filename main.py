import datetime
import openpyxl
import os
import getopt
import sys
import traceback
import importlib
import logging
import logging.handlers
# My modules
import modules.filehandler
import modules.processor
import modules.twitter
import modules.logs
import modules.settings

# Get commandline arguments
try:
    options, remainder = getopt.getopt(sys.argv[1:],'t:ipv', ['ticker=','verbose','nointeract','prod'])
except getopt.GetoptError as e:
      print(e.msg)
      print ('\nUsage: main.py [-t <ETF Ticker>] [-i, -p, -v]')
      print ('--ticker, -t: Specific ETF ticker symbol')
      print ('--verbose, -v: Debug output')
      print ('--nointeract, -i: Non-interactive run (tweets without prompt)')
      print ('--prod, -p: Run using the production Twitter credentials')
      sys.exit(2)

# Set arg switches
nonInteractive = False
chosenEtf = None
prodRun = False
streamLevel = "INFO"
for opt, arg in options:
    if ((opt == '-t' or opt == '--ticker') and not arg.isspace()): # Run the passed ETF        
        chosenEtf = arg
    elif opt == '-i' or opt == '--nointeract': # Run in non-interactive mode
        nonInteractive = True
    elif opt == '-v' or opt == '--verbose':
        streamLevel = "DEBUG"
    elif opt == '-p' or opt == '--prod':
        prodRun = True

# Log config
logger = modules.logs.setupLogger(__name__, modules.settings.logFormat, 
                                    modules.settings.streamFormat, modules.settings.logDateFormat, 
                                    modules.settings.streamDateFormat, streamLevel,
                                    modules.settings.logDebugFile, modules.settings.logInfoFile)
# Setup the basic log config to catch debug output from third-party modules
# logging.basicConfig(format=logFormat, datefmt=logDateFormat, level=os.environ.get("LOGLEVEL", "INFO") )
logger.info(f"Logfiles established: {modules.settings.logDebugFile} | {modules.settings.logInfoFile}")

trackedEtfs = ['POTX','CNBS', 'YOLO', 'MJ', 'MSOS'] #Update by hand for now. Also determines order 
trackedEtfCount = len(trackedEtfs)

# Run for one if a ticker is specified, otherwise run for all etfs
etfs = []
if chosenEtf is None:
    logger.info(f'Running for ALL ETFs') 
    etfs = trackedEtfs
else:
    logger.info(f'Running for ONE ETF: ${chosenEtf}')
    etfs = [chosenEtf]
    
for etfTicker in etfs:
    logger.info(f'Starting the ${etfTicker} ETF')  
    etf = importlib.import_module(etfTicker) #This loads the etf-specific module and runs any code not in a function

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

    # Run common logic and ETF-specific functions
    try:
        # Auth with Twitter
        api = modules.twitter.auth(prodRun)
        logger.info("Logged in as " + api.me()._json['name'])

        # Download the latest CSV
        modules.filehandler.collectcsv(fileLocTemp, url)

        wbNew = openpyxl.Workbook()
        sheetNew = wbNew.active
        date = ''

        # Collect the date and holdings rows from the CSV
        sheetNew, date, header = etf.date_and_rows(sheetNew, header)

        # Get the previous day's sheet, taking weekends/holidays into account
        wbOld, dateOld = modules.filehandler.previous_day(oldsheet_date_format, oldsheetDateRegex, holdingsRoot, datetime.datetime.strptime(today, modules.settings.common_date_format), 5)
        sheetOld = wbOld.active

        # If the dates on both the latest and last sheet are the same, assume no updates from the fund and exit
        if date == dateOld:
            if os.path.exists(fileLocTemp):
                os.remove(fileLocTemp)
            logger.critical(f"The latest ${etfTicker} sheet has the same date ({date}) as the last ({dateOld}), doing nothing for now..")
            continue

        # Resize new sheet columns and save it
        sheetNew = modules.filehandler.resize_columns(sheetNew)
        wbNew.save(fileLocNew)
        os.remove(fileLocTemp)  

        # Convert Excel sheet to img for tweet attachment
        modules.filehandler.excel_screenshot(fileLocNew, imgFileLocNew)
        
        # Setup dictionaries with old and new sets of ticker/share# pairs
        newPairs, oldPairs = modules.processor.pair_separation(sheetNew, sheetOld, TickerColumn, SharesColumn, rowStart, rowModifier)

        #Separate out newly opened, closed, and updated positions
        diffList, openedList, closedList = modules.processor.position_changes(newPairs, oldPairs, etfTicker)

        tweet = ['']
        lastPage = 0
        if ( not bool(diffList) 
                and not bool(openedList) 
                and not bool(closedList) ):    
            tweet = [f'{header}\n\nNo changes today!']
            logger.info(f"TWEET: There was no difference in ${etfTicker} holdings for {dateOld}(insheet) and {date}(insheet). Sending the 'no changes' tweet.")                
        else:
            # Build up the tweet message 
            tweet, lastPage = modules.processor.tweet_builder(diffList, openedList, closedList, header)

        # Add a page number if there are more than one pages (280 chars max per tweet)
        tweet = modules.processor.tweet_paginator(lastPage, tweet)    

        # Check for duplicate tweets
        try:
            modules.twitter.dupe_check(api, trackedEtfCount*2, tweet[0])
        except Exception as e:
            logger.critical(e)       
            continue
        
    except Exception as e:
        logger.critical(f"Something went wrong BEFORE TWEETING, finished with ${etfTicker}...")
        logger.critical(e)
        traceback.print_exc()
        continue

    if modules.processor.query_yes_no("Ready to tweet?"):
        modules.twitter.pic_and_tweet(api, imgFileLocNew, tweet)
        logging.info(f"TWEET: Holdings tweet sent for ${etfTicker}. Make sure you commit the new files!")
    else:
        logging.info(f"No tweet sent. Finished with ${etfTicker}...")

logging.shutdown()
exit(0)