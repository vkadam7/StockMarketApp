from flask import Flask, session, render_template, request, redirect, url_for
import pyrebase
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

dbfire = firestore.client() #firestore database

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
db1 = firebase.database()

app.secret_key = "aksjdkajsbfjadhvbfjabhsdk"

persons = {"logged_in": False,"uName": "", "uEmail": "", "uID": ""}

"""
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
"""



@app.route('/')
def hello(name=None):
    return render_template('home.html')

@app.route("/login", methods = ["POST","GET"])
def login():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        passw = result["password"]
        try:
            user = authen.sign_in_with_email_and_password(email,passw)
            print("Log in succesful")
            return render_template('home.html') # this will be a placeholder until I get the database up and running 
        except:
            print("invalid")
            return render_template('register.html')
    else:
        print("didn't work")
        return render_template('login.html')
            


    #return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
