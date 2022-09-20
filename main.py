from re import M
from flask import Flask, session, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_login import (UserMixin, login_user, logout_user, login_required)
from flask import redirect, url_for, request
import pyrebase

app = Flask(__name__)

config = {
'apiKey': "AIzaSyCLXmXYf9D0k_frKUquLoXPofRsWfwP3po",
'authDomain': "stockmarketapp-bb30c.firebaseapp.com",
'projectId': "stockmarketapp-bb30c",
'storageBucket': "stockmarketapp-bb30c.appspot.com",
'messagingSenderId': "873475091746",
'appId': "1:873475091746:web:08017b0f8ad6a57cf5497b",
'measurementId': "G-XVH9S3L9JM",
'databaseURL' : 'https://stockmarketapp-bb30c-default-rtdb.firebaseio.com/'
}

firebase = pyrebase.initialize_app(config)
authen = firebase.auth()

app.secret_key = "aksjdkajsbfjadhvbfjabhsdk"


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max = 10)])
    email = StringField('Email', validators = [LENGTH_REQUIRED(min = 3, max = 20)])
    username = StringField('Username', validators = [InputRequired(), Length(min = 3, max = 10)])
    password =  PasswordField('Password', validators=[InputRequired(), Length(min = 3, max = 10)])


@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if(form.validate_on_submit):
        return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    
    return render_template('register.html', form = form)
        
@app.route('/')
def index():
    return render_template('home.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.html'))
    
#place holder until html pages are up
#@app.route('/Home')
#def index():
#    return render_template('Home.html')
=======
@app.route('/')
def hello(name=None):
    return render_template('home.html')


if __name__ == '__main__':
    app.run(port=1111)