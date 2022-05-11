import time
import http.client
from concurrent.futures import ThreadPoolExecutor
# creates a list of values as long as the number of things we want
# in parallel so we could associate an ID to each. More parallelism here.
parallel = 20
runs=[value for value in range(parallel)]
print(runs)
count = 1000
def getpage(id,div):
    try:
        I = id + div
    except IOError:
        I = id + div
    return I

def getpages():
    with ThreadPoolExecutor(max_workers=4) as executor:
        div =[value for value in range(parallel)]
        results=executor.map(getpage, runs,div)
        print(results)
    return results


import json
f = open('data_out.json')
js = json.load(f)
print(type(js['var95'][0]))

