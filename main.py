from flask import Flask, session, render_template, request, redirect
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

#place holder until html pages are up
#@app.route('/Home')
#def index():
#    return render_template('Home.html')

if __name__ == '__main__':
    app.run(port=1111)
