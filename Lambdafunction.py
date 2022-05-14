import json
import random
from concurrent.futures import ThreadPoolExecutor

def calculateVar(mean, std, shots):
	# generate rather larger (simulated) series with same broad characteristics 
      simulated = [random.gauss(mean,std) for x in range(shots)]
      # sort, and pick 95% and 99% losses (not distinguishing any trading position)
      simulated.sort(reverse=True)
      var95 = simulated[int(len(simulated)*0.95)]
      var99 = simulated[int(len(simulated)*0.99)]
	#print(var95, var99) # so you can see what is being produced
      return var95,var99
      
def testmap(mean,std,shots):
      I = mean,std
      return I
 
 
      
def lambda_handler(event, context):
      mean = (event['mean'])
      std = (event['std'])
      shots = int(event['shots'])
      poke = (event['poke'])
      if poke == "beep":
            return "bop"
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
      return (outputjson)