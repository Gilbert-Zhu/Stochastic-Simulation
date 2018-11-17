#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Reference: https://stackoverflow.com/questions/9990789/
# how-to-force-zero-interception-in-linear-regression

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

counts = pd.read_excel('CallCounts.xls') 
N_t = counts.cumsum(axis=1)

x = N_t.mean()
y = N_t.var()

# y = a * x
# x needs to be a column vector:
x = x[:,np.newaxis]
beta, _, _, _ = np.linalg.lstsq(x, y)

plt.plot(x, y, 'bo')
plt.plot(x, beta*x, 'r-')
plt.xlabel("E[N(t)]")
plt.ylabel("Var[N(t)]")
plt.show()
print "Beta =", beta
