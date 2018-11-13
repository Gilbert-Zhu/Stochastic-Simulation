# The TTF example
# Run 100 replciations and estimate time to failure and average number of func. comp. untill failure

import numpy as np
Ylist = [] # list to keep samples of time to failure
Arealist = [] # list to keep samples of average # of func. components
np.random.seed(1) # fix random number seed
numspare = 2 # number of spare machines
for reps in range(0,1000):
	# initialize clock, next events, state
	clock = 0
	S = 1 + numspare
	NextRepair = float('inf')
	NextFailure = np.random.choice([1,2,3,4,5,6], 1)
	# define variables to keep the last state and time,
    # and the area under the sample path
	Slast = S
	Tlast = clock
	Area = 0
	while S > 0: # While system is functional
		# Determine the next event, update state and advance time
		clock = np.min([NextRepair,NextFailure])
		NextEvent = np.argmin([NextRepair,NextFailure])
		if NextEvent == 0: # Repair
			S += 1
			if S < 1 + numspare:
				NextRepair = clock + 2.5
				NextFailure = clock + np.random.choice([1,2,3,4,5,6], 1)
			if S == 1 + numspare:
				NextRepair = float('inf')
		else: # Failure
			S -= 1
			if S >= 1: # not all machines failed
				NextRepair = clock + 2.5
				NextFailure = clock + np.random.choice([1,2,3,4,5,6], 1)
		# update the area udner the sample path
		Area = Area + Slast * (clock - Tlast)
		# record the current time and state
		Slast = S
		Tlast = clock
	# add samples to the lists
	Ylist.append(clock)
	Arealist.append(Area/float(clock))
# print sample averages
variance = np.var(Ylist)
print(np.mean(Ylist),variance,np.mean(Arealist))
