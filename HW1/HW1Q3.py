import numpy as np
np.random.seed(1) # fix random number seed
Xlist = [] # list to keep samples of # customers
Arealist = [] # list to keep samples of average # customers

for reps in range(0,30):
    clock = 0 # initialize clock
    X = 0 # initialize X
    T = 100000 # Total time unit
    NextArrival = np.random.exponential(scale=1/0.8, size=1)
    NextDeparture = float('inf')
    Xlast = X
    Tlast = clock
    Area = 0
    while clock <= T: # simulation time
        clock = np.min([NextArrival,NextDeparture])
        
        if NextArrival < NextDeparture: # A customer arrives
            if X == 0: 
                NextDeparture = clock + np.random.exponential(scale=1.0)
            X += 1
            NextArrival = clock + np.random.exponential(scale=1/0.8)                   
        elif NextArrival == NextDeparture: 
            # Arrival and departure at the same time
            NextArrival = clock + np.random.exponential(scale=1/0.8)
            NextDeparture = clock + np.random.exponential(scale=1.0)            
        else: # A customer leaves
            if X >= 1:
                X -= 1
                NextDeparture = clock + np.random.exponential(scale=1.0)
            else: # empty queue
                NextDeparture = float('inf')
        # update the area udner the sample path
        Area = Area + Xlast * (clock - Tlast)
        # record the current time and state
        Xlast = X
        Tlast = clock
    # add samples to the lists
    Arealist.append(Area/float(clock))
# print sample averages
print(np.mean(Arealist))

        
        
        
        
        
        
        
        
        