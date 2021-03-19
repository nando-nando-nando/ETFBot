# ETFBot
This Twitter bot aggregates information on the daily holdings of various ETFs

<img src="https://user-images.githubusercontent.com/6925409/111731389-fbdc5880-8838-11eb-9e68-38a58dd98428.png" alt="AdvisorShares ETFs logo" height="130" width="250"/> 
$MSOS  $YOLO   
<br><br><br>  
&nbsp;<img src="https://www.amplifyetfs.com/Data/Sites/6/skins/amplify/images/Amplify_logo_main.png" alt="Amplify ETFs logo" height="50" width="200"/> 
$CNBS
<br><br><br>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/GX-Wordmark_ST-OrangeRGB.png/1200px-GX-Wordmark_ST-OrangeRGB.png" alt="Global X ETFs logo" height="100" width="275"/>  
$POTX
<br><br><br>  
                                                                                    

Usage: main.py [-t --ticker <ETF Ticker>] [-i --nointeract] [-p --prod] [-v --verbose])  
      --ticker, -t: ETF ticker symbol. If not present will run for all tickers  
      --nointeract, -i: Non-interactive run (tweets without prompt)  
      --prod, -p: Run using production Twitter credentials  
      --verbose, -v: Debug output  
      
      
      
<br><br><br><br>
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
