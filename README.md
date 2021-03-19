# ETFBot
This bot aggregates information on the daily holdings of various ETFs


Usage: main.py [-t <ETF Ticker>] [-i --nointeract] [-p --prod] [-v --verbose])
      --ticker, -t: ETF ticker symbol. If not present, will run for all tickers
      --nointeract, -i: Non-interactive run (tweets without prompt)
      --prod, -p: Run using production Twitter credentials
      --verbose, -v: Debug output
      

You need to have a settings.py file under /modules that looks like this:


\# Test Credentials  
api_key=''  
api_secret=''  
access_token=''   
access_secret=''  
  
\# Prod Credentials  
api_key_prod=''  
api_secret_prod=''  
access_token_prod=''  
access_secret_prod=''  
  
\# Tracked ETFs  
trackedEtfCount = 4 \#Update by hand for now  
trackedEtfs = ['POTX','CNBS', 'YOLO', 'MSOS']  
  
\# Copy this verbatim if you don't know how to use it  
common_date_format = "%m-%d-%y"  
logFormat = '%(asctime)s | %(module)s | %(name)s |  %(levelname)s: %(message)s'  
streamFormat = '%(asctime)s | %(module)s |  %(levelname)s: %(message)s'  
logDateFormat = '%m/%d/%Y %I:%M:%S %p'  
streamDateFormat = '%I:%M:%S %p'  
logDebugFile = 'logs/DEBUG.log'  
logInfoFile = 'logs/INFO.log'  
