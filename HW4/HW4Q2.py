import VBASim 
import RNG 
import Basic_Classes
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import comb

Clock = 0.0
ZRNG = RNG.InitializeRNSeed()

Queue = Basic_Classes.FIFOQueue()
Wait = Basic_Classes.DTStat()
Longwait = Basic_Classes.DTStat()
Server = Basic_Classes.Resource()
Calendar = Basic_Classes.EventCalendar()

TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []

TheDTStats.append(Wait)
TheDTStats.append(Longwait)
TheQueues.append(Queue)
TheResources.append(Server)

s = 10
Server.SetUnits(s) 
MeanTBA = 1/9.2
MeanST = 1.0
Phases = 3
RunLength = 2500.0
WarmUp = 500.0
n = 1000 # number of replications
AllStats = []

def Arrival():
    VBASim.Schedule(Calendar,"Arrival",RNG.Expon(MeanTBA, 1),Clock)
    Customer = Basic_Classes.Entity(Clock)
    Queue.Add(Customer, Clock) # queue here includes the customers in service
    
    if Server.Busy < Server.NumberOfUnits: # if there is an idle server available
        Server.Seize(1, Clock)
        VBASim.Schedule(Calendar,"EndOfService",RNG.Erlang(Phases,MeanST,2),Clock)

def EndOfService():
    DepartingCustomer = Queue.Remove(Clock)
    waitingtime = Clock - DepartingCustomer.CreateTime
    Wait.Record(waitingtime)
    waitings.append(waitingtime)
    if waitingtime > 3:
        Longwait.Record(waitingtime)
    if Queue.NumQueue() >= Server.NumberOfUnits: # a new service starts
        VBASim.Schedule(Calendar,"EndOfService",RNG.Erlang(Phases,MeanST,2),Clock)
    else:
        Server.Free(1, Clock)

lastwait = [] # records the last customer's waiting time in each replication, to be used in quantile estimation
for reps in range(n):
    Clock = 0.0
    waitings = [] 
    VBASim.VBASimInit(Calendar,TheQueues,TheCTStats,TheDTStats,TheResources,Clock)
    VBASim.Schedule(Calendar,"Arrival",RNG.Expon(MeanTBA, 1),Clock)
    VBASim.Schedule(Calendar,"EndSimulation",RunLength,Clock)
    VBASim.Schedule(Calendar,"ClearIt",WarmUp,Clock) 
    NextEvent = Calendar.Remove()
    Clock = NextEvent.EventTime
    if NextEvent.EventType == "Arrival":
        Arrival()
    elif NextEvent.EventType == "EndOfService":
        EndOfService() 
    elif NextEvent.EventType == "ClearIt":
        VBASim.ClearStats(TheCTStats,TheDTStats,Clock)
    while NextEvent.EventType != "EndSimulation":
        NextEvent = Calendar.Remove()
        Clock = NextEvent.EventTime
        if NextEvent.EventType == "Arrival":
            Arrival()
        elif NextEvent.EventType == "EndOfService":
            EndOfService()
        elif NextEvent.EventType == "ClearIt":
            VBASim.ClearStats(TheCTStats,TheDTStats,Clock)
    lastwait.append(waitings[-1])
    AllStats.append([Wait.Mean(), Queue.Mean(Clock), Server.Mean(Clock), Longwait.N()/Wait.N()])
Results = pd.DataFrame(AllStats, columns=["Average Wait", "Average Number in Queue", "Average Number of Busy Servers", "P(wait > 3 min)"])
print "Wait:", Results.loc[:,"Average Wait"].mean(), Results.loc[:,"Average Wait"].std()
print "Queue-Length:", Results.loc[:,"Average Number in Queue"].mean(), Results.loc[:,"Average Number in Queue"].std()
print "Num Server Busy:", Results.loc[:,"Average Number of Busy Servers"].mean(), Results.loc[:,"Average Number of Busy Servers"].std()

# Probability estimation:
prob = Results.loc[:,"P(wait > 3 min)"].mean()
error1 = 1.96 * math.sqrt(n*prob*(1-prob)/(n-1)) / math.sqrt(n)
CI1 = "(" + str(prob - error1) + ", " + str(prob + error1) + ")"
print "\nProbability:", prob
print "95% CI for P(wait > 3):", CI1

# Quantile estimation: The estimation is simply the 1000*0.95=950th element in the sorted result
# Increasing upper bound and decreasing lower bound until we are 95% percent sure that the 95% quantile is in this range
for i in range (50):
    a = 0
    for j in range(950-i,950+i+1):
        a += comb(n,j)*(0.95**j)*(0.05**(n-j))
    if a >= 0.95:
        break
print "\nLower bound index:", 950-i, "Upper bound index:", 950+i
lastwait.sort()
print "95% quantile:", lastwait[949]
CI2 = "(" + str(lastwait[949-i]) + ", " + str(lastwait[949+i]) + ")"
print "95% CI for 95% quantile:", CI2

# choosing d(Warmup):
b = np.cumsum(waitings)
c = range(1,len(b)+1)
d = b/c
plt.plot(c,d)
plt.xlabel('# Customer')
plt.ylabel('Cummulative average')
plt.plot()

