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

# Testing landing response codes for frontend pages - Muneeb Khan
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
    teststockDefinitions = app.test_client().get("/stockDefinitions")
    assert teststockDefinitions.status_code == 200



if __name__ == '__main__':
    pytest.main()
