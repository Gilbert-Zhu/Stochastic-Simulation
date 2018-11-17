#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

times = pd.read_csv('servicetime_data.csv') 
x = times['ser_time'].values
xvalues = list(x)

times.plot.hist(bins=150)
plt.xlabel('Service Time')
plt.ylabel('Frequency')
plt.show()

logx = np.log(x)

# MLE for Exponential:
rate = len(x)/float(x.sum()) # lambda = n/sum(x)
scale1 = 1.0/rate
loc = 0

# create a Q-Q plot
fig1 = stats.probplot(x, dist="expon", sparams=(loc,scale1), plot=plt)
plt.show()

# perform a goodness of fit test (K-S) test; 
# null hyposthesis is that data is coming from the specified dist
GoF1 = stats.kstest(x, 'expon', args=(loc, scale1))
print GoF1

# MLE for Lognormal:
mu = logx.sum()/len(x)
sigma = np.sqrt(((logx-(logx.sum()/len(x)))**2).sum()/len(x))
shape2 = sigma
scale2 = np.exp(mu)
loc = 0

fig2 = stats.probplot(x, dist="lognorm", sparams=(shape2,loc,scale2), plot=plt)
plt.show()

GoF2 = stats.kstest(x, 'lognorm', args=(shape2, loc, scale2))
print GoF2


# Gamma:
# Since there is no closed form MLE for Gama, we fit a Gamma numerically
shape3, loc, scale3 = stats.gamma.fit(x, floc = 0)

fig3 = stats.probplot(x, dist="gamma", sparams=(shape3,loc,scale3), plot=plt)
plt.show()

GoF3 = stats.kstest(xvalues, 'gamma', args=(shape3, loc, scale3))
print GoF3

# Moments estimation for Gama:
beta = x.std()
alpha = x.mean()/x.std()








