# -*- coding: utf-8 -*-
import VBASim 
import RNG 
import Basic_Classes
import math
import numpy as np
import pandas as pd
from scipy import stats

Clock = 0.0
ZRNG = RNG.InitializeRNSeed()
Queue = Basic_Classes.FIFOQueue() # Inventory
Calendar = Basic_Classes.EventCalendar()
Server = Basic_Classes.Resource() # dummy, not used
TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []
TheQueues.append(Queue)
TheResources.append(Server)
AllStats = []
p = 0.2
MeanTBA = 1.0 # Demand Arrival
MeanLead = 1.0 # Item Arrival
T = 240 # Runlength
s = 4
S = 10
NumSold = 0 # total number of sold items
M = 0 # total number of ordered items
o = 0.5
r = 1
c = 0.2
n = 100 # replications
kappa = 0.01

def DemandArrival():
    global NumSold, M, OrderPlaced, NumtoOrder
    VBASim.Schedule(Calendar,"DemandArrival",RNG.Expon(MeanTBA, 1),Clock)
    B = 1 # generating Geometric r.v.:
    while True:
        if RNG.Uniform(0,1,3) < p:
            break
        else:
            B += 1  
    if Queue.NumQueue() > 0: # if Inventory > 0:
        num = min(B,Queue.NumQueue()) # number of items sold
        NumSold += num
        for i in range (num):
            Queue.Remove(Clock) # reduce inventory
        if Queue.NumQueue() < s and OrderPlaced == 0:
            NumtoOrder = S - Queue.NumQueue()
            VBASim.Schedule(Calendar,"ItemArrival",RNG.Expon(MeanLead, 2),Clock)
            OrderPlaced = 1 # change the state whether an order is placed
            M += NumtoOrder
    
def ItemArrival():
    global NumSold, M, OrderPlaced, NumtoOrder
    for i in range (NumtoOrder):
        Queue.Add(0,Clock)
    OrderPlaced = 0
    if Queue.NumQueue() < s:
        NumtoOrder = S - Queue.NumQueue()
        VBASim.Schedule(Calendar,"ItemArrival",RNG.Expon(MeanLead, 2),Clock)
        OrderPlaced = 1
        M += NumtoOrder
       
def Simulation():
    global NumSold, M, OrderPlaced, NumtoOrder, Clock
    VBASim.VBASimInit(Calendar,TheQueues,TheCTStats,TheDTStats,TheResources,Clock)
    for i in range (S): # Initial inventory is S
        Queue.Add(0,Clock)
    VBASim.Schedule(Calendar,"DemandArrival",RNG.Expon(MeanTBA, 1),Clock)
    VBASim.Schedule(Calendar,"EndSimulation",T,Clock) 
    NextEvent = Calendar.Remove()
    Clock = NextEvent.EventTime
    if NextEvent.EventType == "DemandArrival":
        DemandArrival()
    elif NextEvent.EventType == "ItemArrival":
        ItemArrival() 
    while NextEvent.EventType != "EndSimulation":
        NextEvent = Calendar.Remove()
        Clock = NextEvent.EventTime
        if NextEvent.EventType == "DemandArrival":
            DemandArrival()
        elif NextEvent.EventType == "ItemArrival":
            ItemArrival()          
  
# Problem 1(a):      
for reps in range(n):
    Clock = 0.0
    NumSold = 0
    M = 0
    OrderPlaced = 0 # whether the company has placed an order
    NumtoOrder = 0 # number of items to order    
    Simulation()    
    R = r*NumSold - o*M - c*Queue.Mean(Clock)*T
    AllStats.append([Queue.Mean(Clock), NumSold, M, R])
Results = pd.DataFrame(AllStats, columns=["Avg Inventory","# sold","# ordered","Profit"])
print "\nAvg Inventory:", Results.loc[:,"Avg Inventory"].mean()
print "Avg # sold:", Results.loc[:,"# sold"].mean()
print "Avg # ordered:", Results.loc[:,"# ordered"].mean()
print "Avg Profit:", Results.loc[:,"Profit"].mean()
AvgR = Results.loc[:,"Profit"].mean()
VarR = Results.loc[:,"Profit"].var()*n/(n-1)
a = stats.t.ppf(1-0.025, n-1)*math.sqrt(VarR)/math.sqrt(n)
CI = "(" + str(AvgR - a) + ", " + str(AvgR + a) + ")"
print "95% CI:", CI

# Problem 1(b):
print "\nAchieving desired relative error:"
reps = 1 # Initialize using the last replication result
Profits = np.array(R) 
while True:
    Clock = 0.0
    NumSold = 0
    M = 0
    OrderPlaced = 0 # whether the company has placed an order
    NumtoOrder = 0 # number of items to order
    Simulation()
    R = r*NumSold - o*M - c*Queue.Mean(Clock)*T
    reps += 1
    Profits = np.append(Profits,R)
    AvgR = Profits.mean()
    VarR = Profits.var()*reps/(reps-1)
    a = stats.t.ppf(1-0.025, reps-1)*math.sqrt(VarR)/math.sqrt(reps)
    if a/AvgR <= kappa:
        break
print "Avg Profit:", AvgR
print "Replications:", reps
CI = "(" + str(AvgR - a) + ", " + str(AvgR + a) + ")"
print "95% CI:", CI


# Problem 1(d):
print "\nSelection of the best:"
# Step 1:
n0 = 50
alpha = 0.05
delta = 0.1
K = 5
eta = 0.5*( ((2*alpha)/(K-1))**(-2.0/(n0-1)) - 1 )
t2 = 2*eta*(n0-1)
# Here the initial 0's are just convenient for indexing:
slist = [0,6,4,3,2,2]
Slist = [0,8,6,6,5,6]

# Step 2:
I = [1,2,3,4,5]
Y = pd.DataFrame(np.zeros((n0,K+1))) # storing simulation results for profits
S2 = pd.DataFrame(np.zeros((K+1,K+1))) # S_squared_i,h

for i in range(1,K+1):
    s = slist[i]
    S = Slist[i]
    for j in range(n0):
        Clock = 0.0
        NumSold = 0
        M = 0
        OrderPlaced = 0 # whether the company has placed an order
        NumtoOrder = 0 # number of items to order
        Simulation() 
        R = r*NumSold - o*M - c*Queue.Mean(Clock)*T
        Y.iloc[j,i] = R
        
for i in range(1,K+1):
    for h in range(1,K+1):        
        S2.iloc[i,h] = sum(((Y[i]-Y[h])-(Y[i].mean()-Y[h].mean()))**2)/(n0-1)
rep = n0
Ybar = [0]
for i in I:
    Ybar.append(Y[i].mean())

# Step 3 & 4:
while True:
    # Step 3:
    Iold = I
    for i in Iold:
        for h in Iold: # here it doesn't matter if i == h, no need to ensure i!= h
            W = max(0, 0.5*delta*(t2*S2.iloc[i,h]/delta**2-rep)/rep)
            if Ybar[i] < Ybar[h] - W: # We are maximizing profit, 
                I.remove(i)
                break
    # Step 4:
    if len(I) == 1:
        break
    else:
        for i in I:
            s = slist[i]
            S = Slist[i]
            Clock = 0.0
            NumSold = 0
            M = 0
            OrderPlaced = 0 # whether the company has placed an order
            NumtoOrder = 0 # number of items to order
            Simulation() 
            R = r*NumSold - o*M - c*Queue.Mean(Clock)*T
            Ybar[i] = (Ybar[i]*rep + R)/(rep + 1) # update sample means
        rep += 1
print "Best scenario:", I, "replications:", rep, "\nE[R]:", Ybar[1:]


