#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import VBASim 
import RNG 
import Basic_Classes
import pandas as pd
import csv
Clock = 0.0
ZRNG = RNG.InitializeRNSeed()
'''
Class1   Class2
Queue1   Queue2
   |  \     |
   |   \    |
   A   B1   B2
   |     \  |
   |      \ |
ServerA  ServerB
'''
Queue1 = Basic_Classes.FIFOQueue()
Queue2 = Basic_Classes.FIFOQueue()
ServerA = Basic_Classes.Resource()
ServerB = Basic_Classes.Resource()
TotalTime1 = Basic_Classes.DTStat()
TotalTime2 = Basic_Classes.DTStat()
Calendar = Basic_Classes.EventCalendar()

TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []

TheDTStats.append(TotalTime1)
TheDTStats.append(TotalTime2)
TheQueues.append(Queue1)
TheQueues.append(Queue2)
TheResources.append(ServerA)
TheResources.append(ServerB)

ServerA.SetUnits (1) 
ServerB.SetUnits (1) 
MeanTBA1 = 1.0
MeanTBA2 = 2.5
MeanPT1_1 = 1.0
MeanPT1_2 = 2.0
MeanPT2 = 1.0

RunLength = 55000.0
WarmUp = 5000.0
AllStats = []

def Arrival1():
    VBASim.Schedule(Calendar,"Arrival1",RNG.Expon(MeanTBA1, 1),Clock)
    Customer1 = Basic_Classes.Entity(Clock)
    # Go to A, or go to B, or add in Queue1
    if ServerA.Busy < ServerA.NumberOfUnits: # Go to ServerA
        ServerA.Seize(1, Clock)
        VBASim.SchedulePlus(Calendar,"EndOfServiceA",RNG.Expon(MeanPT1_1,3),Customer1,Clock)
    elif (ServerB.Busy < ServerB.NumberOfUnits) and (Queue1.NumQueue == 0): # Go to ServerB
        ServerB.Seize(1, Clock)
        VBASim.SchedulePlus(Calendar,"EndOfServiceB1",RNG.Expon(MeanPT1_2,4),Customer1,Clock)
    else: # Add in Queue1
        Queue1.Add(Customer1, Clock)
    
def Arrival2():
    VBASim.Schedule(Calendar,"Arrival2",RNG.Expon(MeanTBA2, 2),Clock)
    Customer2 = Basic_Classes.Entity(Clock)
    # Go to B, or add in Queue2
    if ServerB.Busy < ServerB.NumberOfUnits: # Go to ServerB
        ServerB.Seize(1, Clock)
        VBASim.SchedulePlus(Calendar,"EndOfServiceB2",RNG.Expon(MeanPT2,5),Customer2,Clock)
    else: # Add in Queue2
        Queue2.Add(Customer2, Clock)

def EndOfServiceA(DepartingCustomer):
    TotalTime1.Record(Clock - DepartingCustomer.CreateTime)
    if Queue1.NumQueue() > 0: # Go to ServerA
        NextCustomer = Queue1.Remove(Clock)
        VBASim.SchedulePlus(Calendar,"EndOfServiceA",RNG.Expon(MeanPT1_1,3),NextCustomer,Clock)
    else: 
        ServerA.Free(1, Clock)

def EndOfServiceB1(DepartingCustomer):
    TotalTime1.Record(Clock - DepartingCustomer.CreateTime)
    if Queue1.NumQueue() > 0: # Serve Customer from Queue1
        NextCustomer = Queue1.Remove(Clock)
        ServerB.Seize(1, Clock)
        VBASim.SchedulePlus(Calendar,"EndOfServiceB1",RNG.Expon(MeanPT1_2,4),NextCustomer,Clock)
    elif Queue2.NumQueue() > 0: # Serve Customer from Queue2
        NextCustomer = Queue2.Remove(Clock)
        ServerB.Seize(1, Clock)
        VBASim.SchedulePlus(Calendar,"EndOfServiceB2",RNG.Expon(MeanPT2,5),NextCustomer,Clock)
    else:
        ServerB.Free(1, Clock)
# The only difference between EndOfServiceB1 and EndOfServiceB2 is:
# We record TotalTime for Customer Class 1 and 2, respectively
def EndOfServiceB2(DepartingCustomer):
    TotalTime2.Record(Clock - DepartingCustomer.CreateTime)
    if Queue1.NumQueue() > 0:
        NextCustomer = Queue1.Remove(Clock)
        ServerB.Seize(1, Clock)
        VBASim.SchedulePlus(Calendar,"EndOfServiceB1",RNG.Expon(MeanPT1_2,4),NextCustomer,Clock)
    elif Queue2.NumQueue() > 0:
        NextCustomer = Queue2.Remove(Clock)
        ServerB.Seize(1, Clock)
        VBASim.SchedulePlus(Calendar,"EndOfServiceB2",RNG.Expon(MeanPT2,5),NextCustomer,Clock)
    else:
        ServerB.Free(1, Clock)
        
for reps in range(0,20,1):
    print reps+1
    Clock = 0.0
    VBASim.VBASimInit(Calendar,TheQueues,TheCTStats,TheDTStats,TheResources,Clock)

    VBASim.Schedule(Calendar,"Arrival1",RNG.Expon(MeanTBA1, 1),Clock)
    VBASim.Schedule(Calendar,"Arrival2",RNG.Expon(MeanTBA2, 1),Clock)
    VBASim.Schedule(Calendar,"EndSimulation",RunLength,Clock)
    VBASim.Schedule(Calendar,"ClearIt",WarmUp,Clock)

    NextEvent = Calendar.Remove()
    Clock = NextEvent.EventTime
    if NextEvent.EventType == "Arrival1":
        Arrival1()
    elif NextEvent.EventType == "Arrival2":
        Arrival2()
    elif NextEvent.EventType == "EndOfServiceA":
        EndOfServiceA(NextEvent.WhichObject) 
    elif NextEvent.EventType == "EndOfServiceB1":
        EndOfServiceB1(NextEvent.WhichObject)
    elif NextEvent.EventType == "EndOfServiceB2":
        EndOfServiceB2(NextEvent.WhichObject)
    
    while NextEvent.EventType != "EndSimulation":
        NextEvent = Calendar.Remove()
        Clock = NextEvent.EventTime
        if NextEvent.EventType == "Arrival1":
            Arrival1()
        elif NextEvent.EventType == "Arrival2":
            Arrival2()
        elif NextEvent.EventType == "EndOfServiceA":
            EndOfServiceA(NextEvent.WhichObject) 
        elif NextEvent.EventType == "EndOfServiceB1":
            EndOfServiceB1(NextEvent.WhichObject)
        elif NextEvent.EventType == "EndOfServiceB2":
            EndOfServiceB2(NextEvent.WhichObject)
        elif NextEvent.EventType == "ClearIt":
            VBASim.ClearStats(TheCTStats,TheDTStats,Clock)  
    AllStats.append([TotalTime1.Mean(),TotalTime2.Mean(),Queue1.Mean(Clock),Queue2.Mean(Clock),ServerA.Mean(Clock),ServerB.Mean(Clock)])

Results = pd.DataFrame(AllStats, columns=["TotalTime1","TotalTime2","Queue1","Queue2","ServerA","ServerB"])
print Results
# Open a .csv file and write the output to it
myfile = open('Q4.csv','w')
mydata = [["Total Time 1 = ",str(TotalTime1.Mean())],["Total Time 2 = ", str(TotalTime2.Mean())],
            ["Queue 1 = ", str(Queue1.Mean(Clock))], ["Queue 2 = " , str(Queue2.Mean(Clock))],
            ["Server A = ", str(ServerA.Mean(Clock))], ["Server B = " , str(ServerB.Mean(Clock))]]
with myfile:
    writer = csv.writer(myfile)
    writer.writerows(mydata)
