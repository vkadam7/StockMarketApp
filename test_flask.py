import pytest
from main import app, register, login
from asyncio.windows_events import NULL

from datetime import datetime
import math
from operator import itemgetter, mod
import re
from statistics import mean
from datetime import timedelta

from flask import Flask, abort, flash, session, render_template, request, redirect, url_for
import pyrebase
import firebase_admin

from stockSim import Quiz, SimulationFactory, StockData, User, Order, Simulation, Portfolio
from followers import FollowUnfollow, UserInfo
from firebase_admin import firestore
from firebase_admin import credentials
import numpy as np
import pyrebase
import firebase_admin
from firebase_admin import db

# Testing landing response codes for frontend pages - Muneeb Khan
# Successful landing of pages (code 200)
def test_landing():
    testlanding = app.test_client().get("/")
    assert testlanding.status_code == 200

def test_home():
    testhome = app.test_client().get("/home")
    assert testhome.status_code == 200

def test_aboutus():
    testaboutus = app.test_client().get("/aboutus")
    assert testaboutus.status_code == 200

def test_information():
    testinformation = app.test_client().get("/information")
    assert testinformation.status_code == 200

def test_graphPictures():
    testgraphPictures = app.test_client().get("/graphPictures")
    assert testgraphPictures.status_code == 200

def test_stockDefinitions():
    teststockDefinitions = app.test_client().get("/StockDefinitions")
    assert teststockDefinitions.status_code == 200

# Testing Registrations with Email, Username, and Password Validations - Muneeb Khan
# Succesfull registrations will redirect the user to login page (code 302)
# Fail registrations will keep user on registration page (code 200)
def test_register_success():
    user = {"email" : "pytest3@gmail.com",
    "password" : "ABCDEG4$3",
    "confirmPassw" : "ABCDEG4$3",
    "Unames" : "Pytest2",
    "username" : "Pytest2"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 302
    dbfire = firestore.client()
    dbfire.collection('Users').document(user).update({"TestUser" : "True"})

def test_register_fail_usernameInUse():
    user = {"email" : "pytest3@gmail.com",
    "password" : "ABCDEG4$",
    "confirmPassw" : "ABCDEG4$",
    "Unames" : "UnitTesting",
    "username" : "UnitTesting"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 200

def test_register_fail_passwordsDontMatch():
    user = {"email" : "pytest3@gmail.com",
    "password" : "ABCDEG4$",
    "confirmPassw" : "ABCDEG5#",
    "Unames" : "Pytest1",
    "username" : "Pytest1"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 200

def test_register_fail_passwordTooShort():
    user = {"email" : "pytest3@gmail.com",
    "password" : "AB4$",
    "confirmPassw" : "AB4$",
    "Unames" : "Pytest1",
    "username" : "Pytest1"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 200

def test_register_fail_passwordTooLong():
    user = {"email" : "pytest3@gmail.com",
    "password" : "ABCDEFG123$%^IStoolongandover20characters",
    "confirmPassw" : "ABCDEFG123$%^IStoolongandover20characters",
    "Unames" : "Pytest1",
    "username" : "Pytest1"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 200

def test_register_fail_passwordMissingDigit():
    user = {"email" : "pytest3@gmail.com",
    "password" : "ABCDEG$$",
    "confirmPassw" : "ABCDEG$$",
    "Unames" : "Pytest1",
    "username" : "Pytest1"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 200

def test_register_fail_passwordMissingSpecial():
    user = {"email" : "pytest3@gmail.com",
    "password" : "ABCDEG44",
    "confirmPassw" : "ABCDEG44",
    "Unames" : "Pytest12",
    "username" : "Pytest12"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 200

def test_register_fail_blankEmail():
    user = {"email" : "",
    "password" : "ABCDEG4$",
    "confirmPassw" : "ABCDEG4$",
    "Unames" : "Pytest12",
    "username" : "Pytest12"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 200

def test_register_fail_blankPassword():
    user = {"email" : "pytest3@gmail.com",
    "password" : "",
    "confirmPassw" : "",
    "Unames" : "Pytest12",
    "username" : "Pytest12"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 200

def test_register_fail_blankUsername():
    user = {"email" : "pytest3@gmail.com",
    "password" : "ABCDEG4$3",
    "confirmPassw" : "ABCDEG4$3",
    "Unames" : "",
    "username" : "Pytest12"}
    testregister = app.test_client().post("/register", data = user)
    assert testregister.status_code == 200

# Testing Password Recovery with valid, invalid, and missing emails - Muneeb Khan
# Successful Email entry will redirect the user to login page (code 302)
# If unsuccessful however will keep the user on recovery page (code 200)
def test_passwordRecovery_success():
    user = {"email" : "pytest1@gmail.com"}
    testPasswordRecovery = app.test_client().post("/PasswordRecovery", data = user)
    assert testPasswordRecovery.status_code == 302

def test_passwordRecovery_fail_invalidEmail():
    user = {"email" : "fakeEmail@gmail.com"}
    testPasswordRecovery = app.test_client().post("/PasswordRecovery", data = user)
    assert testPasswordRecovery.status_code == 200

def test_passwordRecovery_fail_missingEmail():
    user = {"email" : ""}
    testPasswordRecovery = app.test_client().post("/PasswordRecovery", data = user)
    assert testPasswordRecovery.status_code == 200

# Logout test - Muneeb Khan
# A successful logout will redirect the user to login page (code 302)
def test_logout():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'muneebfkhan93@gmail.com'
    testlogout = client.get("/logout")
    assert testlogout.status_code == 302

# Update Profile tests with validations - Muneeb Khan
# Succuessful profile update will redirect the user to profile page (code 302)
# Failed profile update will keep user on update page (code 200)
def test_updateProfile_success():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'muneebfkhan93@gmail.com'

    user = {"Unames" : "MuneebTestName",
    "experience" : "Experience test update"}
    testupdateProfile = client.post("/update", data = user)
    assert testupdateProfile.status_code == 302

def test_updateProfile_userNameInUse():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'muneebfkhan93@gmail.com'

    user = {"Unames" : "UnitTesting",
    "experience" : "Experience test1"}
    testupdateProfile = client.post("/update", data = user)
    assert testupdateProfile.status_code == 200

def test_updateProfile_fail_missingUserName():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'muneebfkhan93@gmail.com'

    user = {"Unames" : "",
    "experience" : "Test Update eperience"}
    testupdateProfile = app.test_client().post("/update", data = user)
    assert testupdateProfile.status_code == 200

def test_updateProfile_fail_missingExperience():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = "go894@wayne.edu"
    user = {"Unames" : "UnitTesting",
    "experience" : " "}
    testupdateProfile = app.test_client().post("/update", data = user)
    assert testupdateProfile.status_code == 200
    
    
#Login test case- Viraj Kadam
#Fixed by Muneeb Khan
#Status Code = 302: If user login test is successful, the user will be redirected to the profile page
#Status Code = 200: If user login test has failed, then the user will remain on the login page
    
def test_login_successful():
    user = {"email": "muneebfkhan93@gmail.com",
    "password": "ABCDEF2@"}
    testLogin = app.test_client().post("/login", data = user)
    assert testLogin.status_code == 302
   
def test_login_failure_noAccount():
    user = {
        "email": " ", 
        "password": " ", 
    }
    testLogin = app.test_client().post("/login", data = user)
    assert testLogin.status_code == 200

def test_login_failure_invalidEmail():
    user = {"email" : "invalidEmail@gmail.com", 
    "password" : "ABCDEG4$3"}
    testLogin = app.test_client().post("/login", data = user)
    assert testLogin.status_code == 200

def test_login_failure_missingEmail():
    user = {"email" : " ", 
    "password" : "ABCDEG4$3"}
    testLogin = app.test_client().post("/login", data = user)
    assert testLogin.status_code == 200

def test_login_failure_missingPassword():
    user = {"email" : "go8940@wayne.edu", 
    "password" : " "}
    testLogin = app.test_client().post("/login", data = user)
    assert testLogin.status_code == 200
    
    
def test_login_failure_invalidPassword():
    user = {"email": "muneebfkhan93@gmail.com",
    "password": "invalidPassword"}
    testLogin = app.test_client().post("/login", data = user)
    assert testLogin.status_code == 200

def test_stockSearch_successful():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = "go8940@wayne.edu"
            session['stockNames'] = "Ford"
        testUser = client.post("/stockSearch", data = session['stockNames'])
        assert testUser.status_code == 302

def test_stockSearch_failure():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = "go8940@wayne.edu"
            session['stockNames'] = " "
        testUser = client.post("/stockSearch", data = session['stockNames'])
        assert testUser.status_code == 200
#Author: Viraj Kadam
#Test cases for follow and unfollow functions

def test_UserSearch():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = "go8940@wayne.edu"
        testUser = client.post("/social", data = {"userName" : "viraj1"})
        assert testUser.status_code == 302
        
def test_UserSearch_failure():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = "go8940@wayne.edu"
        testUser = client.post("/social", data = {"userName": " "})
        assert testUser.status_code == 200


def test_Follow_successful():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = "go8940@wayne.edu"
        testUser = client.post("/follow", data = {"userName" : "viraj1"})
        assert testUser.status_code == 302

def test_Unfollow_successful():
     with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = "go8940@wayne.edu"
        testUser = client.post("/unfollow", data = {"userName" : "viraj1"})
        assert testUser.status_code == 302

#Social System test cases
def test_blog_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'miqdadhafiz35@gmail.com'
    testuser = client.post("/postBlog", data = {"blogPost":"This post comes from the test file."})
    assert testuser.status_code == 302

def test_Blog():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'miqdadhafiz35@gmail.com'
            session['stockNames'] = "BlackRock Capital Investment Corporation"
    testuser = client.get("/Blog")
    assert testuser.status_code == 200

def test_userPosts():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'miqdadhafiz35@gmail.com'
            session['stockNames'] = "BlackRock Capital Investment Corporation"
    testuser = client.get("/userPosts")
    assert testuser.status_code == 200

def test_Leaderboard():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'miqdadhafiz35@gmail.com'
            session['stockNames'] = "BlackRock Capital Investment Corporation"
    testuser = client.get("/Leaderboard")
    assert testuser.status_code == 200

def test_edit():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'miqdadhafiz35@gmail.com'
            session['postID'] = "Jp0h4YgXepatDz4bzaDD"
    testuser = client.post("/editingPost", data = {"editingthePost":"This post edits from the test file."})
    assert testuser.status_code == 302

def test_editPage():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'miqdadhafiz35@gmail.com'
    testuser = client.get("/editPost", query_string = {"postID": "Jp0h4YgXepatDz4bzaDD"})
    assert testuser.status_code == 200

def test_delete():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = 'miqdadhafiz35@gmail.com'
    testuser = client.get("/postDelete", query_string = {"postID": "Jp0h4YgXepatDz4bzaDD"})
    assert testuser.status_code == 302


if __name__ == '__main__':
    pytest.main()
