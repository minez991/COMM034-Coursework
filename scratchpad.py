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




list1 = [1, 2, 3]
list2 = [4, 5, 6]

# `zipped_lists` contains pairs of items from both lists.
# Create a list with the sum of each pair.
sum = [x + y for (x, y) in zip(list1, list2)] 

print(sum)
# [5, 7, 9]

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
