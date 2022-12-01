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

from stockSim import Quiz, SimulationFactory, StockData, User, Order, Simulation, portfolio
from followers import FollowUnfollow, UserInfo
from firebase_admin import firestore
from firebase_admin import credentials
import numpy as np
import pyrebase
import firebase_admin
from firebase_admin import db

@pytest.fixture()
def client():

    client = app.test_client()

    yield client

#Test responses for landing pages - Muneeb Khan
def test_home_page(client):
    testget = client.get("/home")
    assert testget.status_code == 200

def test_aboutus_page(client):
    testget = client.get("/aboutus")
    assert testget.status_code == 200

def test_information_page(client):
    testget = client.get("/information")
    assert testget.status_code == 200


# Test cases for registration and validations for email, password, and username - Muneeb Khan
# Successful registration test
def test_register_success(client):

    testregisteruser = client.post("/register", data = {"email" : "Unittest123456@gmail.com",
    "password" : "ABCDEF4$",
    "confirmPassw" : "ABCDEF4$",
    "Unames" : "UnitTesting3",
    "username" : "UnitTesting3"})
    assert testregisteruser.status_code == 302 # Redirects user to profile page code 302

# Unsuccesful registration tests
def test_register_invalidpassword_missingspecial(client):

    testregisteruser = client.post("/register", data = {"email" : "sample123459@gmail.com",
    "password" : "ABCDEF3",
    "confirmPassw" : "ABCDEF3",
    "Unames" : "Samples",
    "username" : "Samples"})
    assert testregisteruser.status_code == 200 # Keeps user on register page code 200

def test_register_invalidpassword_missingdigit(client):

    testregisteruser = client.post("/register", data = {"email" : "sample123459@gmail.com",
    "password" : "ABCDEF#",
    "confirmPassw" : "ABCDEF#",
    "Unames" : "Samples",
    "username" : "Samples"})
    assert testregisteruser.status_code == 200 # Keeps user on register page code 200

def test_register_invalidpassword_tooshort(client):

    testregisteruser = client.post("/register", data = {"email" : "sample123459@gmail.com",
    "password" : "AB1@",
    "confirmPassw" : "AB1@",
    "Unames" : "Samples",
    "username" : "Samples"})
    assert testregisteruser.status_code == 200 # Keeps user on register page code 200

def test_register_invalidpassword_toolong(client):

    testregisteruser = client.post("/register", data = {"email" : "sample123459@gmail.com",
    "password" : "ABCDEF#istoolongandover20characters",
    "confirmPassw" : "ABCDEF#istoolongandover20characters",
    "Unames" : "Samples",
    "username" : "Samples"})
    assert testregisteruser.status_code == 200 # Keeps user on register page code 200

def test_register_invalidemail(client):

    testregisteruser = client.post("/register", data = {"email" : "sample1234.com",
    "password" : "ABCDEF3#",
    "confirmPassw" : "ABCDEF3#",
    "Unames" : "Samples",
    "username" : "Samples"})
    assert testregisteruser.status_code == 200 # Keeps user on register page code 200

def test_register_invalidusername(client):

    testregisteruser = client.post("/register", data = {"email" : "sample1234@gmail.com",
    "password" : "ABCDEF3#",
    "confirmPassw" : "ABCDEF3#",
    "Unames" : "UnitTesting",
    "username" : "UnitTesting"})
    assert testregisteruser.status_code == 200 # Keeps user on register page code 200

#Test cases for Password recovery - Muneeb Khan
#Succesful Password recovery test
def test_passwordRecoverySuccess(client):
    testpasswordRecovery = client.post("/PasswordRecovery", data = {"email" : "muneebfkhan93@gmail.com"})
    assert testpasswordRecovery.status_code == 302 # Redirect user to login code 302

#Unsuccesful Password recovery tests
def test_passwordRecoveryFail(client):
    testpasswordRecovery = client.post("/PasswordRecovery", data = {"email" : "failemail@gmail.com"})
    assert testpasswordRecovery.status_code == 200 # Keep user on Password recovery page code 200

def test_passwordRecoveryNoEmail(client):
    testpasswordRecovery = client.post("/PasswordRecovery")
    assert testpasswordRecovery.status_code == 400 # Throw a bad request error code 400 for empty email field

if __name__ == '__main__':
    pytest.main()
