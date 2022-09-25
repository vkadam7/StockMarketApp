import StockData

class Order:
    def __init__(self, db, stock, user, index, buyOrSell, quantity, stockPrice):
        self.db = db
        self.stock = stock
        self.user = user
        self.dayOfPurchase = index
        self.option = buyOrSell
        self.quantity = quantity
        self.avgStockPrice = stockPrice
        self.totalPrice = quantity*stockPrice

    def buyOrder(self):
        if self.option == 'buy':
            count = len(self.db.child('Orders').child(self.user.username).get().val())
            orderName = self.ticker + chr(count)
            data = {
                'validity': 'true',
                'ticker': self.stock.ticker,
                'dayOfPurchase': self.dayOfPurchase,
                'buyOrSell': 'buy',
                'quantity': self.quantity,
                'avgStockPrice': self.avgStockPrice,
                'totalPrice': self.totalPrice
            }
            self.db.child('Orders').child(self.user.username).child(orderName).set(data)
        else: return -1

    def sellOrder(self):
        if self.option == 'sell':
            tempInitialQuant = self.quantity
            tempData = self.db.child('Orders').child(self.user.username).get().val()
            listOfChangedOrders = []
            partialOrderFlag = False
            try:
                i = 0
                while tempInitialQuant > 0:
                    orderName = self.ticker + chr(i)
                    tempOrder = tempData[orderName]
                    if tempOrder['validity'] == 'true':
                        if tempOrder['buyOrSell'] == 'buy':
                            tempCheck = tempInitialQuant - tempOrder['quantity']
                            if tempCheck < 0:
                                partialOrderFlag = True
                                finalOrderName = orderName
                                while tempCheck < 0:
                                    tempCheck += 1
                                updatedQuantity = tempCheck
                            tempInitialQuant -= tempOrder['quantity']
                            listOfChangedOrders.append(orderName)
                    i += 1
                totalPrices = []
                #stockPrices = []
                for order in listOfChangedOrders:
                    tempOrder = self.db.child('Orders').child(order).get().val()
                    totalPrices.append(tempOrder['totalPrice'])
                    #stockPrices.append(tempOrder['avgStockPrice'])
                    updatedOrder = {
                        'validity': 'false',
                        'ticker': tempOrder['ticker'],
                        'dayOfPurchase': tempOrder['dayOfPurchase'],
                        'buyOrSell': 'buy',
                        'quantity': tempOrder['quantity'],
                        'avgStockPrice': tempOrder['avgStockPrice'],
                        'totalPrice': tempOrder['totalPrice']
                    }
                    self.db.child('Orders').child(order).update(updatedOrder)
                if partialOrderFlag:
                    finalOrder = self.db.child('Orders').child(finalOrderName).get().val()
                    totalPrices.append(finalOrder['totalPrice'])
                    #stockPrices.append(finalOrder['avgStockPrice'])
                    updatedFinalOrderOriginal = {
                        'validity': 'false',
                        'ticker': finalOrder['ticker'],
                        'dayOfPurchase': finalOrder['dayOfPurchase'],
                        'buyOrSell': 'buy',
                        'quantity': finalOrder['quantity'],
                        'avgStockPrice': finalOrder['avgStockPrice'],
                        'totalPrice': finalOrder['totalPrice']
                    }
                    self.db.child('Orders').child(order).update(updatedFinalOrderOriginal)
                    updatedFinalOrderNew = {
                        'validity': 'true',
                        'ticker': finalOrder['ticker'],
                        'dayOfPurchase': finalOrder['dayOfPurchase'],
                        'buyOrSell': 'buy',
                        'quantity': updatedQuantity,
                        'avgStockPrice': finalOrder['avgStockPrice'],
                        'totalPrice': finalOrder['totalPrice']
                    }
                    count = len(self.db.child('Orders').child(self.user.username).get().val())
                    orderName = finalOrder['ticker'] + chr(count)
                    self.db.child('Orders').child(self.user.username).child(orderName).set(updatedFinalOrderNew)
                sellOrderData = {
                    'validity': 'true',
                    'ticker': self.stock.ticker,
                    'dayOfPurchase': self.dayOfPurchase,
                    'buyOrSell': 'sell',
                    'quantity': self.quantity,
                    'avgStockPrice': self.avgStockPrice,
                    'totalPrice': self.totalPrice
                }
                count = len(self.db.child('Orders').child(self.user.username).get().val())
                orderName = self.ticker + chr(count)
                self.db.child('Orders').child(self.user.username).child(orderName).set(sellOrderData)
                profit = sum(totalPrices) - self.totalPrice
                return profit
            except IndexError:
                return -2
        else: return -1
