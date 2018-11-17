#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import VBASim 
import RNG 
import Basic_Classes
import pandas as pd
Clock = 0.0
ZRNG = RNG.InitializeRNSeed()
Queue = Basic_Classes.FIFOQueue()
Wait = Basic_Classes.DTStat()
Server = Basic_Classes.Resource()
Calendar = Basic_Classes.EventCalendar()
TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []
TheDTStats.append(Wait)
TheQueues.append(Queue)
TheResources.append(Server)
s = 6 # number of servers, to be changed to see results
Server.SetUnits(s) 
MeanTBA = 1.0
MeanST1 = 5.0*1.05
MeanST2 = 5.0*1.05
Phase1, Phase2 = 2, 3
AllStats = []
T = 480
Total_Customer1, Total_Customer2 = 0, 0
counts = pd.read_excel('CallCounts.xls') 
rates = counts.mean()

def Arrival():
    VBASim.Schedule(Calendar,"Arrival",RNG.Expon(60.0/rates[int(Clock/60.0)],1),Clock)
    Customer = Basic_Classes.Entity(Clock)
    Queue.Add(Customer, Clock)
    if Server.Busy < Server.NumberOfUnits: 
        # if not all servers are busy, we can schedule a service
        Server.Seize(1, Clock)
        if Uniform(0,1,1) < 0.59: # 59% Financial Customer
            VBASim.Schedule(Calendar,"EndOfService1",RNG.Erlang(Phase1,MeanST1,2),Clock)
        else:
            VBASim.Schedule(Calendar,"EndOfService2",RNG.Erlang(Phase2,MeanST2,3),Clock)

def EndOfService1():
    global Total_Customer1
    Total_Customer1 += 1
    DepartingCustomer1 = Queue.Remove(Clock)
    Wait.Record(Clock - DepartingCustomer1.CreateTime)
    if Queue.NumQueue() >= Server.NumberOfUnits:
        if Uniform(0,1,1) < 0.59:
            VBASim.Schedule(Calendar,"EndOfService1",RNG.Erlang(Phase1,MeanST1,2),Clock)
        else:
            VBASim.Schedule(Calendar,"EndOfService2",RNG.Erlang(Phase2,MeanST2,3),Clock)
    else:
        Server.Free(1, Clock)
        
def EndOfService2():
    global Total_Customer2
    Total_Customer2 += 1
    DepartingCustomer2 = Queue.Remove(Clock)
    Wait.Record(Clock - DepartingCustomer2.CreateTime)
    if Queue.NumQueue() >= Server.NumberOfUnits:
        if Uniform(0,1,1) < 0.59:
            # if there are enough customers waiting, we can schedule a service
            VBASim.Schedule(Calendar,"EndOfService1",RNG.Erlang(Phase1,MeanST1,2),Clock)
        else:
            VBASim.Schedule(Calendar,"EndOfService2",RNG.Erlang(Phase2,MeanST2,3),Clock)
    else:
        Server.Free(1, Clock)
        
        
for reps in range(0,100,1):
    Total_Customer1 = 0
    Total_Customer2 = 0
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
            
    AllStats.append([Wait.Mean(),Queue.Mean(Clock),Server.Mean(Clock),Total_Customer1,
                     Total_Customer2,Total_Customer1+Total_Customer2])
    print reps+1
Results = pd.DataFrame(AllStats, columns=["Wait","Queue","Server","Customer1","Customer2","Total Customer"])
print Results
print "Wait:", Results.loc[:,"Wait"].mean(), Results.loc[:,"Wait"].std()
print "Queue-Length:", Results.loc[:,"Queue"].mean(), Results.loc[:,"Queue"].std()
print "Utilization:", Results.loc[:,"Server"].mean(), Results.loc[:,"Server"].std()
print "Customer1:", Results.loc[:,"Customer1"].mean(),"Customer2:",Results.loc[:,"Customer2"].mean(), \
    "Total Customer:",Results.loc[:,"Total Customer"].mean()

