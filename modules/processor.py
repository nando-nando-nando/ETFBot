import locale
import logging
import modules.logs
import modules.settings
# Log config
logger = logging.getLogger(__name__)

# row_start - the first row above the tickers and shares held, typically the header row
def pair_separation(sheetNew, sheetOld, tickerKey, sharesKey, row_start, row_modifier):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF8')

    # Setup dictionaries with old and new sets of ticker/share# pairs
    newPairs = dict()
    oldPairs = dict()

    # print("\n\nNew pairs: \n")
    row = row_start
    for cell in sheetNew[tickerKey]:
                
        # If the row is empty or has unexpected values, move on. Otherwise, add it to the pairs list
        if  ( not cell.value #These rules are just an aggregate of all tracked ETFs. TODO:Move these to their respective ETFs.
                or len(cell.value) < 2 
                or row <= row_start 
                or "Ticker" in cell.value 
                or "None" in str(sheetNew[f'{sharesKey}{row}'].value) ):
            # print(str(sheetNew[f'B{row}'].value))
            row = row+1
            pass
        else:
            newPairs[cell.value] = int(locale.atof(str(sheetNew[f'{sharesKey}{row - row_modifier}'].value)))
            # print(f'{cell.value}:{newPairs[cell.value]}')
            row = row+1
        # print(str(sheetNew[f'B{row}'].value))
   
    # print("\n\nOld pairs: \n")
    row = row_start
    for cell in sheetOld[tickerKey]:
        
        # If the row is empty or has unexpected values, move on. Otherwise, add it to the pairs list
        if  ( not cell.value 
                or len(cell.value) < 2 
                or row <= row_start 
                or "Ticker" in cell.value 
                or "None" in str(sheetOld[f'{sharesKey}{row}'].value) ):
            # print(str(sheetOld[f'B{row}'].value))
            row = row+1
            pass
        else:
            oldPairs[cell.value] = int(locale.atof(str(sheetOld[f'{sharesKey}{row - row_modifier}'].value)))
            # print(f'{cell.value}:{oldPairs[cell.value]}')
            row = row+1
        # print(str(sheetOld[f'B{row}'].value))

    return newPairs, oldPairs

# Pairs should be dictionaries in a 'Ticker':'SharesHeld' format
def position_changes(newPairs, oldPairs, etfTicker):
    diffList = dict()
    openedList = dict()
    closedList = dict()

    # Separate out newly opened, closed, and updated positions    
    for ticker in newPairs:
        if ticker in oldPairs:
            # Calculate the change in position value
            diff = (int(float(newPairs[ticker])) - int(float(oldPairs[ticker])))
            if diff != 0:
                diffList[ticker] = diff
        else: 
            openedList[ticker] = newPairs[ticker]
            
    for ticker in oldPairs:
        if ticker not in newPairs:
            closedList[ticker] = oldPairs[ticker]
    logger.info(f"${etfTicker} position changes:")
    logger.info(diffList)
    logger.info(openedList)
    logger.info(closedList)
    return diffList, openedList, closedList

def tweet_builder(diffList, openedList, closedList, tweetHeader):
    # Build the tweet message, paginate if necessary
    tweet = [tweetHeader]
    page = 0
    if bool(diffList):
        tweet[page] = tweet[page] + '\n\nPosition Changes\n' 
        for ticker in diffList:
            if len(tweet[page]) >= 240:
                page = page + 1
                tweet.append('')
            tweet[page] = tweet[page] + f'\n  ${ticker.ljust(10)}' + f'{diffList[ticker]:,d}'
    if bool(openedList):
        if len(tweet[page]) >= 240:
            page = page + 1
            tweet.append('')
            tweet[page] = tweet[page] + 'Opened Positions\n'
        else:
            tweet[page] = tweet[page] + '\n\nOpened Positions\n' 
        for ticker in openedList:
            if len(tweet[page]) >= 240:
                page = page + 1
                tweet.append('')
            tweet[page] = tweet[page] + f'\n  ${ticker.ljust(10)}' + f'{openedList[ticker]:,d}'
    if bool(closedList):
        if len(tweet[page]) >= 240:
            page = page + 1
            tweet.append('')
            tweet[page] = tweet[page] + 'Closed Positions\n' 
        else:
            tweet[page] = tweet[page] + '\n\nClosed Positions\n'
        for ticker in closedList:
            if len(tweet[page]) >= 240:
                page = page + 1
                tweet.append('')
            tweet[page] = tweet[page] + f'\n  ${ticker.ljust(10)}' + f'{closedList[ticker]:,d}'
    return tweet, page

def tweet_paginator(lastPage, tweet):
    if (lastPage>0):
        pageCount = 0
        while pageCount <= lastPage:
            # Add the page number
            tweet[pageCount] = tweet[pageCount] + f'\n\n{pageCount+1}/{lastPage+1}' 
            print(tweet[pageCount])
            pageCount = pageCount + 1
    else:
        print(tweet[0])
    return tweet

import sys
# Taken from: https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
def query_yes_no(question, default="no"):
    # Ask a yes/no question via raw_input() and return their answer.

    # "question" is a string that is presented to the user.
    # "default" is the presumed answer if the user just hits <Enter>.
    #     It must be "yes" (the default), "no" or None (meaning
    #     an answer is required of the user).

    # The "answer" return value is True for "yes" or False for "no".    
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")