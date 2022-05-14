 
import cgitb
import os
import html
import cgi
import cgitb
import json
import random
from concurrent.futures import ThreadPoolExecutor

cgitb.enable()

def calculateVar(mean, std, shots):
	# generate rather larger (simulated) series with same broad characteristics 
      simulated = [random.gauss(mean,std) for x in range(shots)]
      # sort, and pick 95% and 99% losses (not distinguishing any trading position)
      simulated.sort(reverse=True)
      var95 = simulated[int(len(simulated)*0.95)]
      var99 = simulated[int(len(simulated)*0.99)]
	#print(var95, var99) # so you can see what is being produced
      return var95,var99

form = cgi.FieldStorage()


mean = form.getvalue("mean")
std = form.getvalue("std")
shots = form.getvalue("shots")

mean = float(mean)
std = float(std)

var95 = []
var99 = []
shot_array = [0]*len(mean)
for i in range(len(mean)):
      shot_array[i] = shots
      
with ThreadPoolExecutor() as executor:
      results = executor.map(calculateVar,mean,std,shot_array)

for r in results:
      var95.append(r[0])
      var99.append(r[1])

outputjson = {
      'var95': var95,
      'var99': var99
}

print("Content-Type: text/html;charset=utf-8")
print("")
print (str(mean) + " " + str(std))
print(outputjson)