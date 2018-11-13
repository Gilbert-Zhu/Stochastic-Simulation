'''
MIE1613 HW1 Q1 by Xiaotian Zhu 1003250545
'''

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(1)
numsim = 100000

a = np.random.exponential(scale=5.0, size=numsim) - 2
a[a < 0] = 0 # max(a,0)

avg = a.mean()
variance = np.var(a)
# calculating cumulative average values:
b = np.cumsum(a)
c = range(1,numsim+1)
d = b/c

plt.plot(c,d)
plt.xlabel('# Simulations')
plt.ylabel('Cummulative average')
plt.plot([0,100000], [3.3516,3.3516], color='r', linestyle='-', linewidth=2)

print avg, variance


