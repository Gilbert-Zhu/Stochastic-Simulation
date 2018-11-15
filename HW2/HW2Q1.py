# -*- coding: utf-8 -*-

import RNG
import math
import pandas as pd
import matplotlib.pyplot as plt

ZRNG = RNG.InitializeRNSeed()
Replications = 10000
Maturity = 1.0
Steps = 40
Sigma = 0.4
InterestRate = 0.05
InitialValue = 30.0
StrikePrice = 40.0
Interval = Maturity / Steps
b = 70.0 # upper barrier
delta_tau = 0.1 # interval for tau's
ValueList = [] # List to keep the option value for each

for i in range(0,Replications):
    X = InitialValue
    PriceList = [] # a list to store stock prices at different steps
    for j in range(0,Steps):
        Z = RNG.Normal(0,1,1)
        X = X*math.exp((InterestRate-Sigma**2/2)*Interval+Sigma*math.sqrt(Interval)*Z)
        PriceList.append(X)
    Indicator = 1 # Initialize Indicator function
    for k in range(int(Maturity/delta_tau)): # for all pre-specified times
        if PriceList[int(delta_tau/Interval)*k + 3] >= b: # the (4k+3)rd item in PriceList
            Indicator = 0
            break
    Value = Indicator * math.exp(-InterestRate * Maturity) * max(X - StrikePrice, 0)
    ValueList.append(Value)    

#plt.hist(ValueList,bins = range(30))
plt.hist(ValueList, bins=range(int(math.ceil(max(ValueList)))))
plt.xlabel('Payoff')
plt.ylabel('Frequency')
ValueList = pd.DataFrame(ValueList,columns=["Option Value"])
print "Mean", ValueList.mean()
print "Sd", ValueList.std()
plt.show()

