from .models import User
import numpy as np
from sklearn.linear_model import LogisticRegression
from .twitter import vectorize_tweet

def predict_user(user0_username, user1_username, hypo_tweet_text):

    # query users from db
    user0 = User.query.filter(User.username==user0_username).one()
    user1 = User.query.filter(User.username==user1_username).one()

    # get word embeddings from user's tweets
    user0_vect = np.array([tweet.vect for tweet in user0.tweets])
    user1_vect = np.array([tweet.vect for tweet in user1.tweets])

    # combine vectorizations into matrix
    X = np.vstack([user0_vect, user1_vect])

    # create prediction vector
    y = np.concatenate([np.zeros(len(user0.tweets)), np.ones(len(user1.tweets))])

    # instantiate linear regression model
    log_reg = LogisticRegression()
    # train model
    log_reg.fit(X, y)

    # vectorize hypothetical tweet
    hypo_tweet_vect = np.array([vectorize_tweet(hypo_tweet_text)])

    # generate prediction
    prediction = log_reg.predict(hypo_tweet_vect)

    return prediction[0]