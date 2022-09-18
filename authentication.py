from distutils.command.config import config
import pyrebase

config = {
'apiKey': "AIzaSyCLXmXYf9D0k_frKUquLoXPofRsWfwP3po",
'authDomain': "stockmarketapp-bb30c.firebaseapp.com",
'projectId': "stockmarketapp-bb30c",
'storageBucket': "stockmarketapp-bb30c.appspot.com",
'messagingSenderId': "873475091746",
'appId': "1:873475091746:web:08017b0f8ad6a57cf5497b",
'measurementId': "G-XVH9S3L9JM",
'databaseURL' : ''
}

firebase = pyrebase.initialize_app(config)
authen = firebase.auth()


email = 'testing@gmail.com'
password = '12345'

#These are a some functions to help us interact with the database 

#user = authen.create_user_with_email_and_password(email,password)
#print(user)

#user = authen.sign_in_with_email_and_password(email,password)

#userInfo = authen.get_account_info(user['idToken'])
#print(info)

#authen.send_email_verification(user['idToken'])

#authen.send_password_reset_email(email)