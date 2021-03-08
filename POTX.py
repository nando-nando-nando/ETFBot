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
    oldsheet_date_format = insheet_date_format
    oldsheetDateRegex = r'\d{2}\/\d{2}\/\d{4}'
    today = datetime.datetime.now().strftime(settings.common_date_format)
    yesterday = (datetime.datetime.now() - datetime.timedelta(1)).strftime(settings.common_date_format)
    holdingsRoot = "holdings/potx"
    fileLocTemp = f"{holdingsRoot}/{today}.csv"
    fileLocNew = f"{holdingsRoot}/{today}.xlsx"
    fileLocOld = f"{holdingsRoot}/{yesterday}.xlsx"
    imgFileLocNew = f"{holdingsRoot}/imgs/GlobalX_POTX_Holdings_{today}.png"
    url = "https://www.globalxetfs.com/funds/potx/?download_full_holdings=true"
    header = f'The latest @GlobalXETFs $POTX holdings are out🌿\n#potstocks\n{yesterday}\n\n'
    # Pair Separation Variables
    TickerColumn = 'B'
    SharesColumn = 'F'
    rowStart = 2
    rowModifier = 1


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
                # pp.pprint(row[0])
                match = re.search(r'\d{1,2}\/\d{1,2}\/\d{4}', row[0]) 
                if  match is not None: #Get the date           
                    date = datetime.datetime.strptime(match.group(), insheet_date_format).date().strftime(settings.common_date_format)
                if "information" not in row[0] and row[2] != "CASH": #Get the holdings rows
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

    #Convert Excel sheet to img for tweet attachment
    import excel2img
    excel2img.export_img(fileLocNew,imgFileLocNew,None, None)

    # Setup dictionaries with old and new sets of ticker/sharesheld pairs
    newPairs, oldPairs = processor.pair_separation(sheetNew, sheetOld, TickerColumn, SharesColumn, rowStart, rowModifier)

    # Separate out opened, closed, and updated positions
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

# twitter.pic_and_tweet(api, imgFileLocNew, tweet)