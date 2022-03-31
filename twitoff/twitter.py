import tweepy
from os import getenv
from .models import DB, Tweet, User
import spacy


# Get our API keys (without exposing them)
key = getenv("TWITTER_API_KEY")
secret = getenv("TWITTER_API_KEY_SECRET")


# authenticate with twitter
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)

# opens a connection to the API
TWITTER = tweepy.API(TWITTER_AUTH)

def add_or_update_user(username):
    try:
        # get the user data from twitter
        twitter_user = TWITTER.get_user(screen_name=username)

        # check to see if user is already in database
        #   if already in db: do nothing
        #   if not in db: insert user
        db_user = (User.query.get(twitter_user.id) or
                User(id=twitter_user.id, username=username))

        # adds user
        #   if user exists, updates user
        #   (does not duplicate users)
        DB.session.add(db_user)

        # get the user's tweets from their timeline
        tweets = twitter_user.timeline(count=200,
                                    exclude_replies=True,
                                    include_rts=False,
                                    tweet_mode='extended',
                                    since_id=db_user.newest_tweet_id)

        # assign newest_tweet_id
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # adds tweets to db
        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id,
                            text=tweet.full_text[:300],
                            user_id = db_user.id,
                            vect=tweet_vector)
            
            DB.session.add(db_tweet)

    except Exception as error:
        print(f'Error when processing {username}: {error}')
        raise error

    # commit db changes
    DB.session.commit()

# load nlp model
nlp = spacy.load('my_model/')

# use nlp to vectorize tweet
def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector