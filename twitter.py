import tweepy
import settings

# Returns the api handler for making tweepy calls
def auth():
    auth = tweepy.OAuthHandler(settings.api_key, settings.api_secret)
    auth.set_access_token(settings.access_token, settings.access_secret)

    api = tweepy.API(auth)
    if api.verify_credentials() == False:
        raise Exception("Credential verification failed. Check your creds in settings.py")
    else:
        return api
