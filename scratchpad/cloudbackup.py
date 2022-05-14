#!/usr/bin/python3
import cgitb
import json
cgitb.enable()

body = {
    'mean' : 0.2,
    'std' : 0.3,
    'shots' : 0.2,
    'poke' : "0.2"
}

print ("Status: 200 OK")
print ("Content-Type: application/json")
print ("Content-Length: %d" % (len(body)))
print ("")
print (json.JSONEncoder().encode(body))



js = {
'mean' : 0,
'std' : 0,
'shots' : 0,
'poke' : "beep"
}
js = json.dumps(js)


import http.client
c = http.client.HTTPConnection("ec2-54-226-18-213.compute-1.amazonaws.com", timeout = 120)
c.request("POST", "/jsontest.py",js)
response = c.getresponse()
data = response.read().decode('utf-8')

json2 = json.loads(data)
print(json2['mean'])



#!/usr/bin/python3
import cgitb
import json
cgitb.enable()

body = {
    'mean' : 0.2,
    'std' : 0.3,
    'shots' : 0.2,
    'poke' : "0.2"
}

print ("Status: 200 OK")
print ("Content-Type: application/json")
print ("")
print (json.dumps(body))
