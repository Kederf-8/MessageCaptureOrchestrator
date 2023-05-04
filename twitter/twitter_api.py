import tweepy
import configparser

# read configs
config = configparser.ConfigParser(
    allow_no_value=True, interpolation=configparser.ExtendedInterpolation()
)
config.read("twitter/config.ini")
section = "twitter2"

api_key = config[section]["api_key"]
api_key_secret = config[section]["api_key_secret"]
bearer_token = config[section]["bearer_token"]

access_token = config[section]["access_token"]
access_token_secret = config[section]["access_token_secret"]

# Authenticate with the Twitter API using Tweepy
auth = tweepy.AppAuthHandler(api_key, api_key_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Set the search query you want to use
query = "#examplehashtag OR keyword"

# Use the Tweepy Cursor object to search for tweets
tweets = tweepy.Cursor(api.search_tweets, q=query).items()

# Print the text of each tweet
for tweet in tweets:
    print(tweet.text)
