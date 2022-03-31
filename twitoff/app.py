from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .twitter import add_or_update_user
from .predict import predict_user
from os import getenv

def create_app():

    APP = Flask(__name__)

    # tell our app where to find our database
    APP.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')
    APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # link (initialize) app to database
    DB.init_app(APP)

    @APP.route("/")
    def home():
        # query the database for all users
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @APP.route("/reset")
    def reset():
        # drops DB tables
        DB.drop_all()
        # Creates tables according to the classes in models.py
        DB.create_all()
        return render_template('base.html', title='Reset DB')
    
    # @APP.route('/populate')
    # def populate():
    #     add_or_update_user('nasa')
    #     return render_template('base.html', title='Populate')

    @APP.route('/update')
    def update():
        usernames = [user.username for user in User.query.all()]
        for username in usernames:
            add_or_update_user(username)
        return render_template('base.html', title='Update')

    @APP.route('/user', methods=['POST'])
    @APP.route('/user/<username>', methods=['GET'])
    def user(username=None, message=''):
        if request.method == 'GET':
            tweets = User.query.filter(User.username==username).one().tweets

        if request.method == 'POST':
            tweets = []
            try:
                username = request.values['user_name']
                add_or_update_user(username)
                message=f'User {username} successfully added'
            except Exception as e:
                message = f'Error adding {username} : {e}'
            
        return render_template('user.html',
                                title=username,
                                tweets=tweets,
                                message=message)

    @APP.route('/compare', methods=['POST'])
    def compare():
        user0 = request.values['user0']
        user1 = request.values['user1']

        if user0 == user1:
            message = 'Cannot compare a user to themselves'
        else:
            text = request.values['tweet_text']
            prediction = predict_user(user0, user1, text)
            message = '"{}" is more likely to be said by {} than {}'.format(
                        text,
                        user1 if prediction else user0,
                        user0 if prediction else user1
                        )
        return render_template('prediction.html',
                                title='Prediction',
                                message=message)

    return APP
