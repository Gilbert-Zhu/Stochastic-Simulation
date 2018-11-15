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
s = 3 # number of servers, s = 1, 2, 3
Server.SetUnits(s) 
MeanTBA = 1.0
MeanST = 0.8*s # tau/s = 0.8
Phases = 3
RunLength = 55000.0
WarmUp = 5000.0
AllStats = []

def Arrival():
    VBASim.Schedule(Calendar,"Arrival",RNG.Expon(MeanTBA, 1),Clock)
    Customer = Basic_Classes.Entity(Clock)
    Queue.Add(Customer, Clock)
    if Server.Busy < Server.NumberOfUnits: 
        # if not all servers are busy, we can schedule a service
        Server.Seize(1, Clock)
        VBASim.Schedule(Calendar,"EndOfService",RNG.Erlang(Phases,MeanST,2),Clock)

def EndOfService():
    DepartingCustomer = Queue.Remove(Clock)
    Wait.Record(Clock - DepartingCustomer.CreateTime)
    if (Queue.NumQueue() >= Server.NumberOfUnits):
        # if there are enough customers waiting, we can schedule a service
        VBASim.Schedule(Calendar,"EndOfService",RNG.Erlang(Phases,MeanST,2),Clock)
    else:
        Server.Free(1, Clock)

for reps in range(0,10,1):
    Clock = 0.0
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
    AllStats.append([Wait.Mean(), Queue.Mean(Clock), Server.Mean(Clock)])
    print reps+1
Results = pd.DataFrame(AllStats, columns=["Average Wait", "Average Number in Queue", "Server Utilization"])
print Results
print "Wait:", Results.loc[:,"Average Wait"].mean(), Results.loc[:,"Average Wait"].std()
print "Queue-Length:", Results.loc[:,"Average Number in Queue"].mean(), Results.loc[:,"Average Number in Queue"].std()
print "Utilization:", Results.loc[:,"Server Utilization"].mean(), Results.loc[:,"Server Utilization"].std()