# -*- coding: utf-8 -*-

import RNG
import math
import numpy as np
from scipy.stats import norm
from scipy import stats

ZRNG = RNG.InitializeRNSeed()
n = 10000
T = 1.0
m = 32
vol = 0.3
r = 0.05
X0 = 50.0
K = 55.0
Interval = T/m
alpha = 0.05

T2 = (m+1)*Interval/2.0
Sigma2 = (2*m+1)*vol*vol/(3.0*m)
delta = (vol*vol - Sigma2)/2.0
d = (math.log(X0/K)+(r-delta+Sigma2/2)*T2)/(math.sqrt(Sigma2*T2))
muvc = math.exp(-delta*T2)*X0*norm.cdf(d) - math.exp(-r*T2)*K*norm.cdf(d-math.sqrt(Sigma2*T2))

vList = [] # List to keep the option values
vcList = [] # List to keep vc values

for i in range(n):
    Sum = 0.0
    Product = 1.0
    X = X0
    for j in range(m):
        Z = RNG.Normal(0,1,1)
        X = X * math.exp((r - vol**2/2) * Interval + vol * math.sqrt(Interval) * Z)
        Sum = Sum + X
        Product = Product * X
    v = math.exp(-r * T) * max(Sum/m - K, 0)
    vc = math.exp(-r * T) * max(Product**(1.0/m) - K, 0)
    vList.append(v)    
    vcList.append(vc)

vList = np.array(vList)
vcList = np.array(vcList)
vbar = vList.mean()
vcbar = vcList.mean()

print "v Mean", vList.mean()
print "v Std", vList.std()
print "vc Mean", vcList.mean()
print "vc Std", vcList.std()

beta1 =  sum(np.multiply(vList-vbar,vcList-vcbar))/sum((vcList-vcbar)**2)
beta0 = vbar - beta1*(vcbar-muvc)
part1 = sum((vList - beta0 - beta1*(vcList-muvc))**2)/(n-2.0)
part2 = 1.0/n + (vcbar-muvc)**2/sum((vcList-vcbar)**2)
SIGMA = part1 * part2

error = stats.t.ppf(1-alpha/2,n-2) * math.sqrt(SIGMA)
CI = "(" + str(beta0 - error) + ", " + str(beta0 + error) + ")"
print "m =", m, ", CI:", CI











