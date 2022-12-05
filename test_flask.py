import pytest
from main import app, register, login
from asyncio.windows_events import NULL
#from crypt import methods
#from crypt import methods
#from re import T
from datetime import datetime
import math
from operator import itemgetter, mod
import re
from statistics import mean
from datetime import timedelta
#from django.shortcuts import render
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


if __name__ == '__main__':
    pytest.main()
