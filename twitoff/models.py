from flask_sqlalchemy import SQLAlchemy

# creating database and connecting to it.
DB = SQLAlchemy()


class User(DB.Model):
    # id
    id = DB.Column(DB.BigInteger, primary_key=True)
    # username
    username = DB.Column(DB.String, nullable=False)
    # tweets
    #   not an actual attribute, comes from DB.backref in Tweet class

    # newest tweet id
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return f"<User: {self.username}>"


class Tweet(DB.Model):
    # id
    id = DB.Column(DB.BigInteger, primary_key=True)
    # text
    text = DB.Column(DB.Unicode(300))
    # user_id
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    # user
    #   going to add an attribute to both tables
    #   two-way relationship
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    # place to store our word embeddings "vectorization"
    vect = DB.Column(DB.PickleType, nullable=False)

    def __repr__(self):
        return f"<Tweet: {self.text}>"