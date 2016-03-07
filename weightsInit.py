import random

initPosPnts = [[[0 for i in range (0, 64)] for j in range (0, 6)] for k in range (0, 2)]
finalPosPnts = [[[0 for i in range (0, 64)] for j in range (0, 6)] for k in range (0, 2)]
#a[i + 64*j + 64*6*k] - rolling
#Just use 3 loops for unrolling

f = open("weights.py", "w")
f.write("initPosPnts = " + str(initPosPnts) + "\nfinalPosPnts = " + str(finalPosPnts))
f.close()