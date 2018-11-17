#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import RNG 
import math
import matplotlib.pyplot as plt

times = pd.read_csv('servicetime_data.csv') 
x = list(times['ser_time'].values)
m = len(x)
x.append(0)
x.sort()

def Generate_Samples():
    global x
    global m
    u = Uniform(0,1,1)
    i = int(math.ceil((m-1)*u))
    return x[i] + (m-1)*(x[i+1]-x[i-1])*(u-float(i-1)/(m-1))

samples = []
for j in range(m):
    samples.append(Generate_Samples())

samples = pd.DataFrame(samples,columns=['service time'])    
samples.plot.hist(bins=150)
plt.xlabel('Service Time')
plt.ylabel('Frequency')
plt.show()