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

try:
    pp = pprint.PrettyPrinter(indent=4)

    # Filenames
    insheet_date_format = "%m/%d/%Y"
    oldsheet_date_format = "%Y-%m-%d"
    oldsheetDateRegex = r'\d{4}-\d{1,2}-\d{1,2}'
    today = datetime.datetime.now().strftime(settings.common_date_format)
    yesterday = (datetime.datetime.now() - datetime.timedelta(3)).strftime(settings.common_date_format)
    holdingsRoot = "holdings/msos"
    fileLocTemp = f"{holdingsRoot}/{today}.csv"
    fileLocNew = f"{holdingsRoot}/{today}.xlsx"
    fileLocOld = f"{holdingsRoot}/{yesterday}.xlsx"
    imgFileLocNew = f"{holdingsRoot}/imgs/AdvisorShares_MSOS_Holdings_{today}.png"
    url = "https://advisorshares.com/wp-content/uploads/csv/holdings/AdvisorShares_MSOS_Holdings_File.csv"
    header = f'Hey #MSOGang, the latest @AdvisorShares $MSOS holdings are out🌿🇺🇸\n{today}\n\n'
    # Pair Separation Variables
    TickerColumn = 'C'
    SharesColumn = 'F'
    rowStart = 1
    rowModifier = 0

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
    exit()

twitter.pic_and_tweet(api, imgFileLocNew, tweet)