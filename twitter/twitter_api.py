import tweepy
import configparser
import pandas as pd

# read configs
config = configparser.ConfigParser()
config.read("config.ini")
section = "twitter"

api_key = config[section]["api_key"]
api_key_secret = config[section]["api_key_secret"]

access_token = config[section]["access_token"]
access_token_secret = config[section]["access_token_secret"]

# authentication
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.home_timeline()

columns = ["Time", "User", "Tweet"]

data = []

for tweet in public_tweets:
    data.append([tweet.created_at, tweet.user.screen_name, tweet.text])

df = pd.DataFrame(data, columns=columns)

print(df)
