# https://docs.tweepy.org/
import tweepy

auth = tweepy.OAuthHandler('NnYCz4TfZ8CvAC6FclbvOoPbt', 'YntddsBtsGteUX1cr6HI5XZ9TKbjvi88ipbxG38GSDH5Wt8DG5')
auth.set_access_token('2844687729-sZNK15iDEgYo1WBpny0Cu0cAwX3pdmZI5ptcOnR', 'xhr7EBUV2Okp0Oz0BGRDSsdoSfeMxYngjAiw5vntnBHvI')
## First, get the newest and previous workbooks. Find the differences. 


# Filenames
import datetime
time = datetime.datetime.now().strftime("%m-%d-%y")
fileLoc = f"holdings/{time}.xlsx"
imgFileLoc = f"holdings/imgs/AdvisorShares_MSOS_Holdings_{time}.png"

# Collect Excel sheet
import urllib
dls = "https://advisorshares.com/wp-content/uploads/csv/holdings/AdvisorShares_MSOS_Holdings_File.xlsx"
urllib.request.urlretrieve(dls, fileLoc)  # For Python 3

#Convert Excel sheet to img
import excel2img
excel2img.export_img(fileLoc,imgFileLoc,None, None)

#Get differences
from openpyxl import load_workbook
wb = load_workbook(fileLoc)
sheet = wb.active
for cell in sheet['C']:
    if  not cell.value or len(cell.value) < 2:
        pass
    else:
        print(cell.value)
#  print(len(sheet['C']))






#Paginate tweet



# Auth
try:
    api = tweepy.API(auth)
    if api.verify_credentials() == False:
        raise Exception("Couldn't authenticate with Twitter.")
except:
    print("Couldn't authenticate with Twitter.")
    exit()


#Upload image
#Model: {'_api': <tweepy.api.API object at 0x0000025B82EB60A0>, 'media_id': 1362203886765838338, 'media_id_string': '1362203886765838338', 'size': 42703, 'expires_after_secs': 86400, 'image': {'image_type': 'image/png', 'w': 1007, 'h': 562}}
#mediaobj = api.media_upload(imgFileLoc)

#print(mediaobj.__dict__)

#Tweet (280 chars max per tweet)

# try:
#     #api.update_status(status="Testing out the twitter API media upload", media_ids=[mediaobj.media_id_string])
#     status = api.update_status(status="ddddd")
#     print(status.id_str)
#     status = api.update_status(status="this is a reply", in_reply_to_status_id=status.id_str)
# except tweepy.TweepError as e:
#     print(e.__dict__)
#     print(e.api_code) #code 186 is tweet too long