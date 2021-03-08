# https://docs.tweepy.org/
import tweepy
import settings

# Returns the api handler for making tweepy calls
def auth():
    try:
        auth = tweepy.OAuthHandler(settings.api_key, settings.api_secret)
        auth.set_access_token(settings.access_token, settings.access_secret)

        api = tweepy.API(auth)
        if api.verify_credentials() == False:
            raise Exception("Credential verification failed. Check your creds in settings.py")
        else:
            return api
    except Exception as e:
        print("ERROR: Couldn't authenticate with Twitter. ")
        print(e)

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
            print("ERROR: TweepError thrown during tweet:")
            print(e.__dict__)
            print(e.api_code) #code 186 is tweet too long
        except Exception as e:
            print("ERROR: Exception thrown during tweet:")
            print(e.__dict__)