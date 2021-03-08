# https://docs.tweepy.org/
import tweepy
import csv
import datetime
import openpyxl
import settings
import twitter
import pprint
import filehandler
import re
import os
import processor
pp = pprint.PrettyPrinter(indent=4)

# Auth with Twitter
try:
    api = twitter.auth()
    pp.pprint("Logged in as " + api.me()._json['name'])
except Exception as e:
    print("ERROR: Couldn't authenticate with Twitter. ")
    print(e)
    exit()

# Filenames
insheet_date_format = "%m/%d/%Y"
today = datetime.datetime.now().strftime(settings.common_date_format)
yesterday = (datetime.datetime.now() - datetime.timedelta(1)).strftime(settings.common_date_format)
fileLocTemp = f"holdings/potx/{today}.csv"
fileLocNew = f"holdings/potx/{today}.xlsx"
fileLocOld = f"holdings/potx/{yesterday}.xlsx"

imgFileLocNew = f"holdings/potx/imgs/GlobalX_POTX_Holdings_{today}.png"
url = "https://www.globalxetfs.com/funds/potx/?download_full_holdings=true"

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
            match = re.search(r'\d{2}\/\d{2}\/\d{4}', row[0]) 
            if  match is not None: #Get the date           
                date = datetime.datetime.strptime(match.group(), insheet_date_format).date().strftime(settings.common_date_format)
            if "information" not in row[0] and row[2] != "CASH": #Get the holdings rows
                sheetNew.append(row)
except Exception as e:
    print("ERROR: Couldn't collect the date and rows from the latest holdings csv. ")
    print(e)
    exit()

# Get the previous day's sheet, taking weekends/holidays into account
wbOld, dateOld = filehandler.previous_day(insheet_date_format,r'\d{2}\/\d{2}\/\d{4}', "holdings/potx",datetime.datetime.now(), 5)
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

# Setup dictionaries with old and new sets of ticker/share# pairs
newPairs, oldPairs = processor.pair_separation(sheetNew, sheetOld, 'B', 'F', 2, 1)

# #Separate out newly opened, closed, and updated positions
diffList, openedList, closedList = processor.position_changes(newPairs, oldPairs)

tweet = ['']
if ( not bool(diffList) 
        and not bool(openedList) 
        and not bool(closedList) ):    
    tweet = [f'The latest @GlobalXETFs $POTX holdings are out🌿\n#potstocks\n{yesterday}\n\nNo changes today!']
    print(f"TWEET: There was no difference in the holdings for {today} and {yesterday}. \nSending the 'no changes' tweet.")
    # exit()
else:
    # Build up the tweet message 
    tweet, lastpage = processor.tweet_builder(diffList, openedList, closedList, yesterday)

# Add a page number if there are more than one pages (280 chars max per tweet)
if (lastpage>0):
    pageCount = 0
    while pageCount <= lastpage:
        tweet[pageCount] = tweet[pageCount] + f'\n\n{pageCount+1}/{lastpage+1}' 
        print(tweet[pageCount])
        pageCount = pageCount + 1
else:
    print(tweet[0])
        
# #Upload image
# #Model: {'_api': <tweepy.api.API object at 0x0000025B82EB60A0>, 'media_id': 1362203886765838338, 'media_id_string': '1362203886765838338', 'size': 42703, 'expires_after_secs': 86400, 'image': {'image_type': 'image/png', 'w': 1007, 'h': 562}}
# mediaobj = api.media_upload(imgFileLocNew)

# #Send tweet(s)
# replyId = 0
# for pg in tweet:
#     try:
#         if replyId == 0:
#             status = api.update_status(status=pg, media_ids=[mediaobj.media_id_string])
#             replyId = status.id_str
#         else:
#             status = api.update_status(status=pg, in_reply_to_status_id=status.id_str)
#             replyId = status.id_str
#     except tweepy.TweepError as e:
#         print("ERROR during tweet, closing...")
#         print(e.__dict__)
#         print(e.api_code) #code 186 is tweet too long
#         exit()
#     except Exception as e:
#         print("ERROR during tweet, closing...")
#         print(e.__dict__)
#         exit()