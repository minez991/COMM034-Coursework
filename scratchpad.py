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





js = {
'mean' : 0,
'std' : 0,
'shots' : 0
}
'''
js = json.dumps(js)
import http.client
c = http.client.HTTPConnection("ec2-50-19-178-46.compute-1.amazonaws.com", timeout = 120)
c.request.("POST", "/jsontest.py",params=js)
response = c.getresponse()
data = response.read().decode('utf-8')

json2 = json.loads(data)
print(json2['mean'])

'''

js = { 
    "mean": [
        0.02,
        0.03
    ],
    "std": [
        0.03,
        0.04
    ],
    "shots": 80,
    }
print(json.dumps(js))
print(json.dumps(js).replace("\"", "\\\""))

'''
import http.client
import requests
import urllib.parse
f = open('data.json')
js = json.load(f)
js2 = {"js" : json.dumps(js)}
#js = json.dumps(js)
js = urllib.parse.urlencode(js2)
c = http.client.HTTPConnection("ec2-50-19-178-46.compute-1.amazonaws.com", timeout = 120)
c.request("POST", "/CalcVar.py",js)
#c.request("POST", "/inputjson.py",js)
response = c.getresponse()
data = response.read().decode('utf-8')

data = json.loads(data)

print(data['var95'])

'''



import os
os.environ['AWS_SHARED_CREDENTIALS_FILE']='./static/cred' 
# Above line needs to be here before boto3 to ensure cred file is read
# from the right place
import boto3
# Set the user-data we need – use your endpoint
user_data = """#!/bin/bash
wget https://black-machine-340614.ew.r.appspot.com/cacheavoid/setup.sh
bash setup.sh
"""
ec2 = boto3.resource('ec2', region_name='us-east-1')
instances = ec2.create_instances(
 ImageId = 'ami-0c4f7023847b90238', # ubuntu 20.04
 MinCount = 1, 
 MaxCount = 1, 
 InstanceType = 't2.micro', 
 KeyName = 'CCW_KEY', # Make sure you have the named us-east-1kp
 SecurityGroups=['SSH'], # Make sure you have the named SSH
 BlockDeviceMappings = # extra disk
 [ {'DeviceName' : '/dev/sdf', 'Ebs' : { 'VolumeSize' : 10 } } ],
 UserData=user_data # and user-data
 )
# Wait for AWS to report instance(s) ready. 
for i in instances:
 i.wait_until_running()
 # Reload the instance attributes
 i.load()
 print(i.public_dns_name) # ec2 com address