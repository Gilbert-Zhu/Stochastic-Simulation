#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import VBASim 
import RNG 
import Basic_Classes
import pandas as pd
Clock = 0.0
ZRNG = RNG.InitializeRNSeed()
Queue1 = Basic_Classes.FIFOQueue() # Financial
Queue2 = Basic_Classes.FIFOQueue() # Contact Management
Wait = Basic_Classes.DTStat()
Server1 = Basic_Classes.Resource() # Financial
Server2 = Basic_Classes.Resource() # Contact Management
Calendar = Basic_Classes.EventCalendar()
TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []
TheDTStats.append(Wait)
TheQueues.append(Queue1)
TheQueues.append(Queue2)
TheResources.append(Server1)
TheResources.append(Server2)
s1 = 4 
s2 = 3 
Server1.SetUnits(s1) 
Server2.SetUnits(s2) 
MeanTBA = 1.0
MeanST1 = 5.0
MeanST2 = 5.0
Phase1 = 2
Phase2 = 3
AllStats = []
T = 480 # 8 hours * 60 mins
Total_Customer1 = 0 # Financial
Total_Customer2 = 0 # Contact Management

counts = pd.read_excel('CallCounts.xls') 
rates = counts.mean()

def Arrival():
    global Clock, rates
    VBASim.Schedule(Calendar,"Arrival",RNG.Expon(60.0/rates[int(Clock/60.0)],1),Clock)
    Customer = Basic_Classes.Entity(Clock)
    if Uniform(0,1,1) < 0.59: # 59% Financial Customer
        Queue1.Add(Customer, Clock)
        if Server1.Busy < Server1.NumberOfUnits: 
            # if not all servers are busy, we can schedule Service1
            Server1.Seize(1, Clock)
            VBASim.Schedule(Calendar,"EndOfService1",RNG.Erlang(Phase1,MeanST1,2),Clock)
    else:
        Queue2.Add(Customer, Clock)
        if Server2.Busy < Server2.NumberOfUnits: 
            # if not all servers are busy, we can schedule a service
            Server2.Seize(1, Clock)
            VBASim.Schedule(Calendar,"EndOfService2",RNG.Erlang(Phase2,MeanST2,3),Clock)
            
def EndOfService1():
    global Total_Customer1
    Total_Customer1 += 1
    DepartingCustomer1 = Queue1.Remove(Clock)
    Wait.Record(Clock - DepartingCustomer1.CreateTime)
    if Queue1.NumQueue() >= Server1.NumberOfUnits:
        # if there are enough customers waiting, we can schedule a service
        VBASim.Schedule(Calendar,"EndOfService1",RNG.Erlang(Phase1,MeanST1,2),Clock)
    else:
        Server1.Free(1, Clock)

def EndOfService2():
    global Total_Customer2
    Total_Customer2 += 1
    DepartingCustomer2 = Queue2.Remove(Clock)
    Wait.Record(Clock - DepartingCustomer2.CreateTime)
    if Queue2.NumQueue() >= Server2.NumberOfUnits:
        VBASim.Schedule(Calendar,"EndOfService2",RNG.Erlang(Phase2,MeanST2,3),Clock)
    else:
        Server2.Free(1, Clock)
        
for reps in range(0,100,1):
    Total_Customer1, Total_Customer2 = 0,0
    Clock = 0.0
    VBASim.VBASimInit(Calendar,TheQueues,TheCTStats,TheDTStats,TheResources,Clock)
    VBASim.Schedule(Calendar,"Arrival",RNG.Expon(60.0/rates[int(Clock/60.0)], 1),Clock)
    VBASim.Schedule(Calendar,"EndSimulation",T,Clock)
    NextEvent = Calendar.Remove()
    Clock = NextEvent.EventTime
    if NextEvent.EventType == "Arrival":
        Arrival()
    elif NextEvent.EventType == "EndOfService1":
        EndOfService1() 
    elif NextEvent.EventType == "EndOfService2":
        EndOfService2() 
    while NextEvent.EventType != "EndSimulation":
        NextEvent = Calendar.Remove()
        Clock = NextEvent.EventTime
        if NextEvent.EventType == "Arrival":
            Arrival()
        elif NextEvent.EventType == "EndOfService1":
            EndOfService1()
        elif NextEvent.EventType == "EndOfService2":
            EndOfService2()  
    AllStats.append([Wait.Mean(),Queue1.Mean(Clock),Queue2.Mean(Clock),Server1.Mean(Clock),
                     Server2.Mean(Clock),Total_Customer1,Total_Customer2,Total_Customer1+Total_Customer2])
    print reps+1
Results = pd.DataFrame(AllStats, columns=["Wait","Queue1","Queue2","Server1","Server2","Customer1",
                                          "Customer2","Total Customer"])
print Results
print "Wait:", Results.loc[:,"Wait"].mean(), Results.loc[:,"Wait"].std()
print "Queue1-Length:", Results.loc[:,"Queue1"].mean(), Results.loc[:,"Queue1"].std()
print "Queue2-Length:", Results.loc[:,"Queue2"].mean(), Results.loc[:,"Queue2"].std()
print "Utilization1:", Results.loc[:,"Server1"].mean(), Results.loc[:,"Server1"].std()
print "Utilization2:", Results.loc[:,"Server2"].mean(), Results.loc[:,"Server2"].std()
print "Customer1:", Results.loc[:,"Customer1"].mean(),"Customer2:",Results.loc[:,"Customer2"].mean(), \
      "Total Customer:",Results.loc[:,"Total Customer"].mean() 

