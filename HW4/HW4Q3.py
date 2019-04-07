# -*- coding: utf-8 -*-

import RNG
import math
import numpy as np
import matplotlib.pyplot as plt

ZRNG = RNG.InitializeRNSeed()
n = 10000
Maturity = 1.0
Steps = 32
Sigma = 0.3
InterestRate = 0.05
InitialValue = 50.0
StrikePrice = 55.0
Interval = Maturity / Steps

ValueList = [] # List to keep the option value for each
ValueList1 = []
ValueList2 = []
ValueList3 = []

delta1 = 0.05
delta2 = 1.0
delta3 = 2.0

for i in range(n):
    Sum = 0.0
    Sum1 = 0.0
    Sum2 = 0.0
    Sum3 = 0.0

    X = InitialValue
    X1 = X + delta1
    X2 = X + delta2
    X3 = X + delta3
    
    for j in range(0,Steps):
        Z = RNG.Normal(0,1,1)
        factor = math.exp((InterestRate - Sigma**2/2) * Interval + Sigma * math.sqrt(Interval) * Z)
        X = X * factor
        X1 = X1 * factor
        X2 = X2 * factor
        X3 = X3 * factor
        Sum = Sum + X
        Sum1 = Sum1 + X1
        Sum2 = Sum2 + X2
        Sum3 = Sum3 + X3

    Value = math.exp(-InterestRate * Maturity) * max(Sum / Steps - StrikePrice, 0)
    Value1 = math.exp(-InterestRate * Maturity) * max(Sum1 / Steps - StrikePrice, 0)
    Value2 = math.exp(-InterestRate * Maturity) * max(Sum2 / Steps - StrikePrice, 0)
    Value3 = math.exp(-InterestRate * Maturity) * max(Sum3 / Steps - StrikePrice, 0)
    ValueList.append(Value)    
    ValueList1.append(Value1)    
    ValueList2.append(Value2)    
    ValueList3.append(Value3)    

ValueList = np.array(ValueList)
ValueList1 = np.array(ValueList1)
ValueList2 = np.array(ValueList2)
ValueList3 = np.array(ValueList3)


print "Mean", ValueList.mean()
print "Sd", ValueList.std()
plt.show()

FD1 = (ValueList1-ValueList).mean()/delta1
VarFD1 = ((ValueList1-ValueList).var()/delta1**2)*n/(n-1)
FD2 = (ValueList2-ValueList).mean()/delta2
VarFD2 = ((ValueList2-ValueList).var()/delta2**2)*n/(n-1)
FD3 = (ValueList3-ValueList).mean()/delta3
VarFD3 = ((ValueList3-ValueList).var()/delta3**2)*n/(n-1)

a1 = 1.96*math.sqrt(VarFD1)/math.sqrt(n)
a2 = 1.96*math.sqrt(VarFD2)/math.sqrt(n)
a3 = 1.96*math.sqrt(VarFD3)/math.sqrt(n)
CI1 = "(" + str(FD1 - a1) + ", " + str(FD1 + a1) + ")"
CI2 = "(" + str(FD2 - a2) + ", " + str(FD2 + a2) + ")"
CI3 = "(" + str(FD3 - a3) + ", " + str(FD3 + a3) + ")"

print "delta1: ", delta1, "FD1: ", FD1, "Var1: ", VarFD1, "CI1: ", CI1
print "delta2: ", delta2, "FD2: ", FD2, "Var2: ", VarFD2, "CI2: ", CI2
print "delta3: ", delta3, "FD3: ", FD3, "Var3: ", VarFD3, "CI3: ", CI3



