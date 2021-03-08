import locale
# TODO: consolidate this all further

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
        if  ( not cell.value 
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
def position_changes(newPairs, oldPairs):
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
    print("Position changes:")
    print(diffList)
    print(openedList)
    print(closedList)
    return diffList, openedList, closedList

def tweet_builder(diffList, openedList, closedList, date):
# Build the tweet message, paginate if necessary
    tweet = [f'The latest @GlobalXETFs $POTX holdings are out🌿\n#potstocks\n{date}\n\n']
    page = 0
    if bool(diffList):
        tweet[page] = tweet[page] + 'Position Changes\n' 
        for ticker in diffList:
            if len(tweet[page]) >= 240:
                page = page + 1
                tweet.append('')
            tweet[page] = tweet[page] + f'\n  ${ticker.ljust(8)}' + f'{diffList[ticker]:,d}'
    if bool(openedList):
        if len(tweet[page]) >= 240:
            page = page + 1
            tweet.append('')
            tweet[page] = tweet[page] + 'Opened Positions\n'
        else:
            tweet[page] = tweet[page] + '\n\nOpened Positions\n' 
        for ticker in openedList:
            if len(tweet[page]) >= 260:
                page = page + 1
                tweet.append('')
            tweet[page] = tweet[page] + f'\n  ${ticker.ljust(8)}' + f'{openedList[ticker]:,d}'
    if bool(closedList):
        if len(tweet[page]) >= 240:
            page = page + 1
            tweet.append('')
            tweet[page] = tweet[page] + 'Closed Positions\n' 
        else:
            tweet[page] = tweet[page] + '\n\nClosed Positions\n'
        for ticker in closedList:
            if len(tweet[page]) >= 260:
                page = page + 1
                tweet.append('')
            tweet[page] = tweet[page] + f'\n  ${ticker.ljust(8)}' + f'{closedList[ticker]:,d}'
    return tweet, page
    