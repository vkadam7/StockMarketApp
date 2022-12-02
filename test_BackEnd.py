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

def test_CheckDates():
    assert Simulation.checkDates("2000-01-01", "2000-01-02") == True
    assert Simulation.checkDates("2000-01-01", "2000-02-01") == True
    assert Simulation.checkDates("2000-01-01", "2001-01-01") == True
    assert Simulation.checkDates("2000-01-02", "2000-01-01") == False
    assert Simulation.checkDates("2000-02-01", "2000-01-01") == False
    assert Simulation.checkDates("2001-01-01", "2000-01-01") == False

def test_StockSimStartAndFinish():
    testEmail = "gi5631@wayne.edu"
    dbfire = firestore.client() #firestore database
    sim = Simulation(dbfire, "gi5631@wayne.edu", "2020-01-01", "2020-01-14", 100)
    sim.createSim()
    testArr = []
    for entry in dbfire.collection('Simulations').where('user','==',testEmail).where("ongoing","==",True).stream():
        testArr.append(entry.to_dict())
    assert len(testArr) > 0
    testArr = []
    for entry in dbfire.collection('IntradayStockData').where('simulation', '==', sim.simName).stream():
        testArr.append(entry.to_dict())
    assert len(testArr) > 0
    Simulation.finishSimulation(dbfire, sim.simName)
    simulation = dbfire.collection('Simulations').document(sim.simName).get().to_dict()
    assert simulation['ongoing'] == False
    testArr = []
    for entry in dbfire.collection('IntradayStockData').where('simulation', '==', sim.simName).stream():
        testArr.append(entry.to_dict())
    assert len(testArr) == 0
    dbfire.collection('Simulations').document(sim.simName).delete()