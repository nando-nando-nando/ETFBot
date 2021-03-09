# https://docs.tweepy.org/
import tweepy
# My modules
import logging
import modules.logs
import modules.settings

# Log config
logger = logging.getLogger(__name__)

def dupe_check(api, tweetCount, tweetFirstPage):
    # Read in the last few tweets and check for duplicates   
    timeline = api.user_timeline(count=tweetCount, exclude_replies=True, include_rts=False, tweet_mode='extended')
    for status in timeline:
        message = status._json['full_text']    
        if message in tweetFirstPage or tweetFirstPage in message:        
            logger.critical("Duplicate tweet found in timeline, doing nothing for now..")
            logging.shutdown()       
            exit()

# Returns the api handler for making tweepy calls
def auth():
    try:
        auth = tweepy.OAuthHandler(modules.settings.api_key, modules.settings.api_secret)
        auth.set_access_token(modules.settings.access_token, modules.settings.access_secret)

        api = tweepy.API(auth)
        if api.verify_credentials() == False:
            raise Exception("Credential verification failed. Check your creds in modules.settings.py")
        else:
            return api
    except Exception as e:
        logger.critical("ERROR: Couldn't authenticate with Twitter. ")
        logger.critical(e)

def pic_and_tweet(api, imgFileLoc, tweet):
    # mediaObj model: {'_api': <tweepy.api.API object at 0x0000025B82EB60A0>, 
                    # 'media_id': 1362203886765838338, 'media_id_string': '1362203886765838338', 'size': 42703,
                    # 'expires_after_secs': 86400, 'image': {'image_type': 'image/png', 'w': 1007, 'h': 562}}
    
    #Upload image    
    mediaObj = api.media_upload(imgFileLoc)

    #Send tweet and possibly replies 
    replyId = 0
    for pg in tweet:
        try:
            if replyId == 0: #Initial tweet
                status = api.update_status(status=pg, media_ids=[mediaObj.media_id_string])
                replyId = status.id_str
            else: #A reply for every page after
                status = api.update_status(status=pg, in_reply_to_status_id=status.id_str)
                replyId = status.id_str
        except tweepy.TweepError as e:
            logger.critical("ERROR: TweepError thrown during tweet:")
            logger.critical(e.__dict__)
            logger.critical(e.api_code) #code 186 is tweet too long
        except Exception as e:
            logger.critical("ERROR: Exception thrown during tweet:")
            logger.critical(e.__dict__)