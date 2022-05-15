import time
import http.client
from concurrent.futures import ThreadPoolExecutor
import json
import os
os.environ['AWS_SHARED_CREDENTIALS_FILE']='./static/cred'

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

import os
os.environ['AWS_SHARED_CREDENTIALS_FILE']='./static/cred'
import boto3
ec2 = boto3.resource('ec2', region_name='us-east-1')


instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

mylist = [instance for instance in instances]
print(len(mylist))

for instance in instances:
    print(
        "Id: {0}\nPlatform: {1}\nType: {2}\nPublic IPv4: {3}\nAMI: {4}\nState: {5}\n".format(
        instance.id, instance.platform, instance.instance_type, instance.public_ip_address, instance.image.id, instance.state
        )
    )

    print(type(instance.public_dns_name))
'''

import pandas as pd
from pandas_datareader import data as pdr
import boto3
js_base =  []

js2 = {
		'Select' : "EC2",
	"Resource" : 2,
	"LengthOfPriceHistory" : 101,
	"NumberOfData" : 80,
	"BuyOrSell" : "Buy", 
	"Average95" : -0.05,
	"Average99" : -0.10,
	"Time for Audit" : 0.6
		}


js = {
		'Select' : "EC2",
	"Resource" : 4,
	"LengthOfPriceHistory" : 101,
	"NumberOfData" : 80,
	"BuyOrSell" : "Buy", 
	"Average95" : -0.05,
	"Average99" : -0.10,
	"Time for Audit" : 0.6
		}


#### Clear Audit Log ####
'''
js = json.dumps(js)
js = json.loads(js)


js_base = json.dumps(js_base)
js_base =json.loads(js_base)

s3 = boto3.resource('s3')
s3object = s3.Object('stonkbucket', 'audit.json')


filecontent = s3object.get()['Body'].read().decode('utf-8')
print(filecontent)
s3object.put(
    Body=(bytes(json.dumps(js_base).encode('UTF-8')))
)

filecontent = s3object.get()['Body'].read().decode('utf-8')
print(filecontent)

print(time.time())
'''

### Terminate EC2 ###

ec2 = boto3.resource('ec2', region_name='us-east-1')


instances = ec2.instances.all()

mylist = [instance for instance in instances]
print(len(mylist))

for instance in instances:
    print(
        "Id: {0}\nPlatform: {1}\nType: {2}\nPublic IPv4: {3}\nAMI: {4}\nState: {5}\n".format(
        instance.id, instance.platform, instance.instance_type, instance.public_ip_address, instance.image.id, instance.state
        )
    )
    print(instance.terminate())

