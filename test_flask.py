import pytest
from main import app
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

@pytest.fixture
def client():

    client = app.test_client()

    yield client

def test_home_page(client):
    testget = client.get("/home")
    testpost = client.post("/home")
    assert testget.status_code == 200
    assert testpost.status_code == 405

def test_aboutus_page(client):
    testget = client.get("/aboutus")
    testpost = client.post("/aboutus")
    assert testget.status_code == 200
    assert testpost.status_code == 405

def test_information_page(client):
    testget = client.get("/information")
    testpost = client.post("/information")
    assert testget.status_code == 200
    assert testpost.status_code == 405

def test_login():
    test = app.get("/login")
    assert test.email == 'test123@gmail.com'
    assert test.password == 'password1!'

if __name__ == '__main__':
    pytest.main()
