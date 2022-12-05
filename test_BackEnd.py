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

def test_CheckDates():
    assert Simulation.checkDates("2000-01-01", "2000-01-02") == True
    assert Simulation.checkDates("2000-01-01", "2000-02-01") == True
    assert Simulation.checkDates("2000-01-01", "2001-01-01") == True
    assert Simulation.checkDates("2000-01-02", "2000-01-01") == False
    assert Simulation.checkDates("2000-02-01", "2000-01-01") == False
    assert Simulation.checkDates("2001-01-01", "2000-01-01") == False

def test_StockSimStart():
    testEmail = "gi5631@wayne.edu"
    dbfire = firestore.client() #firestore database
    sim = Simulation(dbfire, testEmail, "2020-01-01", "2020-01-14", 100)
    sim.createSim()
    testArr = []
    for entry in dbfire.collection('Simulations').where('user','==',testEmail).where("ongoing","==",True).stream():
        testArr.append(entry.to_dict())
    assert len(testArr) > 0
    testArr = []
    for entry in dbfire.collection('IntradayStockData').where('simulation', '==', sim.simName).stream():
        testArr.append(entry.to_dict())
    assert len(testArr) > 0

def test_BuyOrder():
    testEmail = "gi5631@wayne.edu"
    testTicker = 'F'
    dbfire = firestore.client() #firestore database
    sim = SimulationFactory(dbfire, testEmail)
    sim = sim.simulation
    currentPrice = "%.2f" % round(SimulationFactory(dbfire, testEmail).simulation.currentPriceOf(testTicker), 2)
    assert float(currentPrice) > 5
    assert float(currentPrice) < 15
    portfolioValue, currentCash = Simulation.getPortfolioValue(dbfire,sim.simName)
    assert portfolioValue == 0
    assert currentCash == 100
    order = Order(dbfire, sim.simName, testTicker, 'Buy', 5, currentPrice)
    order.buyOrder()
    portfolioValue, currentCash = Simulation.getPortfolioValue(dbfire,sim.simName)
    assert portfolioValue == 5*float(currentPrice)
    assert currentCash == 100 - 5*float(currentPrice)
    for entry in dbfire.collection('Orders').where('simulation', '==', sim.simName).where('ticker','==',testTicker).where('buyOrSell','==','Buy').stream():
        buyOrder = entry.to_dict()
    assert buyOrder['sold'] == False
    assert buyOrder['quantity'] == 5
    assert buyOrder['avgStockPrice'] == currentPrice
    assert buyOrder['totalPrice'] == float(currentPrice)*5

def test_SellOrder():
    testEmail = "gi5631@wayne.edu"
    testTicker = 'F'
    dbfire = firestore.client() #firestore database
    sim = SimulationFactory(dbfire, testEmail)
    sim = sim.simulation
    currentPrice = "%.2f" % round(SimulationFactory(dbfire, testEmail).simulation.currentPriceOf(testTicker), 2)
    order = Order(dbfire, sim.simName, testTicker, 'Sell', 1, currentPrice)
    order.sellOrder()
    for entry in dbfire.collection('Orders').where('simulation', '==', sim.simName).where('ticker','==',testTicker).where('buyOrSell','==','Sell').stream():
        sellOrder1 = entry
    sellOrder1ID = sellOrder1.id
    sellOrder1 = sellOrder1.to_dict()
    for entry in dbfire.collection('Orders').where('simulation', '==', sim.simName).where('ticker','==',testTicker).where('buyOrSell','==','Buy').stream():
        buyOrder1 = entry
    buyOrder1ID = buyOrder1.id
    buyOrder1 = buyOrder1.to_dict()
    assert sellOrder1['quantity'] == 1
    assert sellOrder1['avgStockPrice'] == currentPrice
    assert sellOrder1['totalPrice'] == float(currentPrice)
    assert sellOrder1['profit'] == float(currentPrice) - float(buyOrder1['avgStockPrice'])
    assert buyOrder1['sold'] == False
    assert buyOrder1['partiallySold'] == True
    assert buyOrder1['newQuantity'] == 4
    portfolioValue, currentCash = Simulation.getPortfolioValue(dbfire,sim.simName)
    assert portfolioValue == 4*float(currentPrice)
    assert currentCash == 100 - 4*float(currentPrice)
    dbfire.collection('Orders').document(sellOrder1ID).delete()
    order = Order(dbfire, sim.simName, testTicker, 'Sell', 4, currentPrice)
    order.sellOrder()
    for entry in dbfire.collection('Orders').where('simulation', '==', sim.simName).where('ticker','==',testTicker).where('buyOrSell','==','Sell').stream():
        sellOrder2 = entry
    sellOrder2 = sellOrder2.to_dict()
    for entry in dbfire.collection('Orders').where('simulation', '==', sim.simName).where('ticker','==',testTicker).where('buyOrSell','==','Buy').stream():
        buyOrder2 = entry
    buyOrder2ID = buyOrder2.id
    buyOrder2 = buyOrder2.to_dict()
    assert sellOrder2['quantity'] == 4
    assert sellOrder2['avgStockPrice'] == currentPrice
    assert sellOrder2['totalPrice'] == float(currentPrice)*4
    assert sellOrder2['profit'] == float(currentPrice)*4 - float(buyOrder1['avgStockPrice'])*4
    assert buyOrder1ID == buyOrder2ID
    assert buyOrder2['sold'] == True
    assert buyOrder2['partiallySold'] == True
    assert buyOrder2['newQuantity'] == 0
    portfolioValue, currentCash = Simulation.getPortfolioValue(dbfire,sim.simName)
    assert portfolioValue == 0
    assert currentCash == 100
    for entry in dbfire.collection('Orders').where('simulation','==',sim.simName).stream():
        dbfire.collection('Orders').document(entry.id).delete()

def test_SellTaxLot():
    testEmail = "gi5631@wayne.edu"
    testTicker = 'F'
    dbfire = firestore.client() #firestore database
    sim = SimulationFactory(dbfire, testEmail)
    sim = sim.simulation
    currentPrice = "%.2f" % round(SimulationFactory(dbfire, testEmail).simulation.currentPriceOf(testTicker), 2)
    assert float(currentPrice) > 5
    assert float(currentPrice) < 15
    portfolioValue, currentCash = Simulation.getPortfolioValue(dbfire,sim.simName)
    assert portfolioValue == 0
    assert currentCash == 100
    order = Order(dbfire, sim.simName, testTicker, 'Buy', 5, currentPrice)
    order.buyOrder()
    for entry in dbfire.collection('Orders').where('simulation', '==', sim.simName).where('ticker','==',testTicker).where('buyOrSell','==','Buy').stream():
        buyOrder1 = entry
    buyID = buyOrder1.id
    portfolioValue, currentCash = Simulation.getPortfolioValue(dbfire,sim.simName)
    assert portfolioValue == 5*float(currentPrice)
    assert currentCash == 100 - 5*float(currentPrice)
    order = Order(dbfire, sim.simName, testTicker, 'Sell', 5, currentPrice)
    Order.sellTaxLot(dbfire, testEmail, sim.simName, buyID)
    for entry in dbfire.collection('Orders').where('simulation', '==', sim.simName).where('ticker','==',testTicker).where('buyOrSell','==','Sell').stream():
        sellOrder1 = entry
    sellOrder1 = sellOrder1.to_dict()
    for entry in dbfire.collection('Orders').where('simulation', '==', sim.simName).where('ticker','==',testTicker).where('buyOrSell','==','Buy').stream():
        buyOrder1 = entry
    buyOrder1 = buyOrder1.to_dict()
    assert sellOrder1['quantity'] == 5
    assert sellOrder1['avgStockPrice'] == currentPrice
    assert buyOrder1['sold'] == True
    portfolioValue, currentCash = Simulation.getPortfolioValue(dbfire,sim.simName)
    assert portfolioValue == 0
    assert currentCash == 100

def test_StockSimFinish():
    testEmail = "gi5631@wayne.edu"
    dbfire = firestore.client() #firestore database
    sim = SimulationFactory(dbfire, testEmail)
    sim = sim.simulation
    Simulation.finishSimulation(dbfire, sim.simName)
    simulation = dbfire.collection('Simulations').document(sim.simName).get().to_dict()
    assert simulation['ongoing'] == False
    testArr = []
    for entry in dbfire.collection('IntradayStockData').where('simulation', '==', sim.simName).stream():
        testArr.append(entry.to_dict())
    assert len(testArr) == 0
    dbfire.collection('Simulations').document(sim.simName).delete()

def test_getPortfolioValues():
    testEmail = "go8940@wayne.edu"
    testTicker = "GOOG"
    dbfire = firestore.client()
    sim = SimulationFactory(dbfire, testEmail)
    sim = sim.simulation
    Simulation.getPortfolioValue(dbfire, sim.simName)
    portfolioValue = Simulation.getPortfolioValue(dbfire, sim.simName)
    currentPrice = "%.2f" % round(SimulationFactory(dbfire, testEmail).simulation.currentPriceOf(testTicker), 2)
    order = Order(dbfire, sim.simName, testTicker, 'Buy', 5, currentPrice)
    order.buyOrder()
    assert portfolioValue == 5*float(currentPrice)

def test_quizSelection():
    testEmail = "go8940@wayne.edu"
    quiz = Quiz()
