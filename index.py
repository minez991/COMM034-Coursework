from concurrent.futures import Executor, ThreadPoolExecutor
from crypt import methods
from doctest import OutputChecker
from importlib import resources
import os
import logging
import math
import random
from threading import Thread
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from pandas_datareader import data as pdr
import json
from flask import Flask, request, render_template
import time
from datetime import datetime
import urllib.parse
import http.client
import boto3

app = Flask(__name__)

os.environ['AWS_SHARED_CREDENTIALS_FILE']='./static/cred'

#########################################################################    
# 					 AWS Related Setting and functions      			#
#########################################################################
Lambda_client = boto3.client('lambda', region_name='us-east-1')

AWS_S3_BUCKET = 's3://stonkbucket'
def PingLambda(id):
	#Quick helper to make the contrainer warmed up
	random_stop()
	js = {
	'mean' : 0,
	'std' : 0,
	'shots' : 0,
	'poke' : "beep"
	}
	js = json.dumps(js)

	t = time.time()
	
	response = Lambda_client.invoke(
	# use your own ARN below
	FunctionName='arn:aws:lambda:us-east-1:564060094405:function:ReturnVarAvg',
	InvocationType='RequestResponse',
	LogType='None',
	Payload=js
	)
	# Ways of working with the response
	r=response['Payload'].read()
	res_json = json.loads(r) # sometimes, it is necessary to use .decode("utf-8"))
	elapsed = time.time() - t
	#if res_json == "bop":
		#print("\n Pinged \n")
	#print('Elapsed: %s' , elapsed)
	return str(id) +" : " +res_json

#Creating EC resources and run a user defined scripts
def create_EC2_resources(id):
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
	for i in instances:
		i.wait_until_running()
		# Reload the instance attributes
		i.load()

	# Wait for AWS to report instance(s) ready. 
	return i

#Terminate ALL EC2 Servers
def Terminate_EC2():
	ec2 = boto3.resource('ec2', region_name='us-east-1')


	instances = ec2.instances.all()

	mylist = [instance for instance in instances]
	print(len(mylist))

	for instance in instances:
		print(instance.terminate())
	return "success"
	


#########################################################################    
# 					 		Helper Functions			      			#
#########################################################################

#Introduce some ramdom stop when sending request to Lambda function
def random_stop():
	Randomtime = random.randrange(0,20) / 200
	time.sleep(Randomtime)

#Update the data grabbed from yahoo
def update_data():
	print("Data Updated")
	# Code from the python script provided in coursework document, get data here
	yf.pdr_override()


	# Get stock data from Yahoo Finance – here, asking for about 10 years of Gamestop
	# which had an interesting time in 2021: https://en.wikipedia.org/wiki/GameStop_short_squeeze 
	today = date.today()
	decadeAgo = today - timedelta(days=3652)

	#Date| Open| High| Low | Close | adj close |Volumn | 
	global data 
	data = pdr.get_data_yahoo('TSLA', start=decadeAgo, end=today)
	# Other symbols: TSLA – Tesla, AMZN – Amazon, NFLX – Netflix, BP.L – BP 

	#print(data.head)
	# Add two columns to this to allow for Buy and Sell signals
	# fill with zero
	data['Buy']=0
	data['Sell']=0

	# Find the 4 different types of signals – uncomment print statements
	# if you want to look at the data these pick out in some another way
	for i in range(len(data)): 
		# Hammer
		realbody=math.fabs(data.Open[i]-data.Close[i])
		bodyprojection=0.3*math.fabs(data.Close[i]-data.Open[i])

		if data.High[i] >= data.Close[i] and data.High[i]-bodyprojection <= data.Close[i] and data.Close[i] > data.Open[i] and data.Open[i] > data.Low[i] and data.Open[i]-data.Low[i] > realbody:
			data.at[data.index[i], 'Buy'] = 1
			#print("H", data.Open[i], data.High[i], data.Low[i], data.Close[i])   

		# Inverted Hammer
		if data.High[i] > data.Close[i] and data.High[i]-data.Close[i] > realbody and data.Close[i] > data.Open[i] and data.Open[i] >= data.Low[i] and data.Open[i] <= data.Low[i]+bodyprojection:
			data.at[data.index[i], 'Buy'] = 1
			#print("I", data.Open[i], data.High[i], data.Low[i], data.Close[i])

		# Hanging Man
		if data.High[i] >= data.Open[i] and data.High[i]-bodyprojection <= data.Open[i] and data.Open[i] > data.Close[i] and data.Close[i] > data.Low[i] and data.Close[i]-data.Low[i] > realbody:
			data.at[data.index[i], 'Sell'] = 1
			#print("M", data.Open[i], data.High[i], data.Low[i], data.Close[i])

		# Shooting Star
		if data.High[i] > data.Open[i] and data.High[i]-data.Open[i] > realbody and data.Open[i] > data.Close[i] and data.Close[i] >= data.Low[i] and data.Close[i] <= data.Low[i]+bodyprojection:
			data.at[data.index[i], 'Sell'] = 1

#"Helper function: Changing a list of floats to single string
def floatListToString(floatList):
	OutputString = ''
	for num in floatList[:-1]:
		OutputString = OutputString + str(num) + ','
	OutputString = OutputString + str(floatList[-1])
	return OutputString

#Averageing a list of numbers
def Average(lst):
    return sum(lst) / len(lst)

#Render webpage
def doRender(tname, values={}):
	if not (os.path.isfile( os.path.join(os.getcwd(), 'templates/'+tname)) ): #No such file
		print("No File")
		return render_template('index.htm')
	return render_template(tname, **values)

#########################################################################    
# 					 		Running Functions			      		#
#########################################################################

######################################################################
#Calculate resutls using lambda functions							 #
#Return: var95: List of risk at variance at 95% for each data point  #
#		 var99  List of risk at variance at 99% for each data point  #
######################################################################
def AskLambda(id,js):
	print("Lambda #"+str(id)+": Making enquires")
	response = Lambda_client.invoke(
	FunctionName='arn:aws:lambda:us-east-1:564060094405:function:ReturnVarAvg',
	InvocationType='RequestResponse',
	LogType='None',
	Payload=js
	)
	# Ways of working with the response
	r=response['Payload'].read()
	res_json = json.loads(r) # sometimes, it is necessary to use .decode("utf-8"))
	return res_json


######################################################################
#Calculate resutls using EC2 resources								 #
#Return: var95: List of risk at variance at 95% for each data point  #
#		 var99  List of risk at variance at 99% for each data point  #
######################################################################
def AskEC2(id,url,js):
	#Send a HTTP requst using urllib to the ec2 servers
	js = urllib.parse.urlencode(js)
	c = http.client.HTTPConnection(url, timeout = 120)
	c.request("POST", "/CalcVar.py",js)
	response = c.getresponse()
	data = response.read().decode('utf-8')
	res_json = json.loads(data)
	return res_json


#Function for invoking Monte-Carlo Risk calculation using Lambda functions
def doMonty_lambda(data,minhistory = 101,shots= 80,BuyorSellOption="Buy",ONLINE_MODE = False):
	import http.client

	shots=int(shots)
	mean = []
	std = []
	dates = []
	#Select Buy or sell table
	if BuyorSellOption == "Buy":
		print("Client wants to buy")
		for i in range(minhistory, len(data)): 
			if data.Buy[i]==1: # if we were only interested in Buy signals
					mean.append(data.Close[i-minhistory:i].pct_change(1).mean())
					std.append(data.Close[i-minhistory:i].pct_change(1).std())
					date = data.index[i].date()
					date = date.strftime("%Y-%m-%d")
					dates.append(date)

	elif BuyorSellOption == "Sell":
		print("Client wants to Sell")
		for i in range(minhistory, len(data)): 
			if data.Sell[i]==1: # if we were only interested in Buy signals
					mean.append(data.Close[i-minhistory:i].pct_change(1).mean())
					std.append(data.Close[i-minhistory:i].pct_change(1).std())
					date = data.index[i].date()
					date = date.strftime("%Y-%m-%d")
					dates.append(date)

	
	elapsed = 0

	if ONLINE_MODE:
		# Create JSON to Lambda Functions	
		js = {
			'mean' : mean,
			'std' : std,
			'shots' : shots,
			'poke' : "no"
		}
		js = json.dumps(js)

		t = time.time()
		
		# Setup arrays for ThreadPoolExecutor
		global Resource
		js = [js] * Resource
		runs=[value for value in range(Resource)]

		#MultiThread to request for results
		print("Parallelising for " + str(Resource) + " Resources")
		with ThreadPoolExecutor(max_workers=Resource) as executor:
			res_json_table =  executor.map(AskLambda,runs,js)


		Var95_Buffer = []
		Var99_Buffer = []
		
		#Loading result obtained from different lambda funciton
		for result in res_json_table:
			Var95_Buffer.append(result['var95'])
			Var99_Buffer.append(result['var99'])

		#Data Processing to find the mean value of var95 and var99 for each signal 
		var95 = pd.DataFrame(Var95_Buffer)
		var95_mean = var95.mean(axis=0)
		var99 = pd.DataFrame(Var99_Buffer)
		var99_mean = var99.mean(axis=0)

		res_json ={
			'var95' : var95_mean.tolist(),
			'var99' : var99_mean.tolist(),
			'SHOT' : shots
		}

		elapsed = time.time() - t
		print('Elapsed: ' , elapsed)

	else:
		#Using demo data
		f = open('data_out.json')
		res_json = json.load(f)
		res_json['SHOT'] = shots


	# Find the average for var95 and 99.
	avg95 = Average(res_json['var95'])
	avg99 = Average(res_json['var99'])
	avg95 = [avg95] * len(res_json['var95'])
	avg99 = [avg99] * len(res_json['var95'])
	print(res_json)
	Server_shots = res_json['SHOT']

	#Formatting result table
	resultlist= []
	for i in range(0,len(avg95)):	
		resultlist.append( [ dates[i],round(res_json['var95'][i],4), round(res_json['var99'][i],3) ])

	OutputTuple = {
		'var95' : floatListToString(res_json['var95']),
		'var99' : floatListToString(res_json['var99']),
		'dates' : dates,
		'avg95' : floatListToString(avg95),
		'avg99' : floatListToString(avg99),
		'resultlist' : resultlist,
		'RequestTime' : elapsed,
		'Server_shots' : Server_shots
		}

	return OutputTuple

#Function for invoking Monte-Carlo Risk calculation using EC2 resources
def doMonty_EC2(data,minhistory = 101,shots= 80,BuyorSellOption="Buy",ONLINE_MODE = False):

	shots=int(shots)
	mean = []
	std = []
	dates = []
	#Select Buy or sell table
	if BuyorSellOption == "Buy":
		print("Client wants to buy")
		#calculate all data to find the mean and std of data
		for i in range(minhistory, len(data)): 
			if data.Buy[i]==1: # if we were only interested in Buy signals
					mean.append(data.Close[i-minhistory:i].pct_change(1).mean())
					std.append(data.Close[i-minhistory:i].pct_change(1).std())
					date = data.index[i].date()
					date = date.strftime("%Y-%m-%d")
					dates.append(date)

	elif BuyorSellOption == "Sell":
		print("Client wants to Sell")
		for i in range(minhistory, len(data)): 
			if data.Sell[i]==1: # if we were only interested in Buy signals
					mean.append(data.Close[i-minhistory:i].pct_change(1).mean())
					std.append(data.Close[i-minhistory:i].pct_change(1).std())
					date = data.index[i].date()
					date = date.strftime("%Y-%m-%d")
					dates.append(date)

	


	if ONLINE_MODE:
			#JSON Data sent to EC2	
		js = {
			'mean' : mean,
			'std' : std,
			'shots' : shots,
		}
		js2 = {"js" : json.dumps(js)}

		t = time.time()

		#Find and count all running EC2 instances
		ec2 = boto3.resource('ec2', region_name='us-east-1')
		instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
		mylist = [instance for instance in instances]
		EC2_count = len(mylist)
		
		#Check if the EC2 count equals or bigger than the rersources request 
		global Resource
		if EC2_count < Resource:
			raise ValueError('ERROR NOT enough EC2 running for the required amount')

		#create a url list for execute
		url_list = []
		for instance in instances:
			url_list.append(instance.public_dns_name)
		
		#Create query list for execute
		js = [js2] * Resource
		runs=[value for value in range(Resource)]

		# Parallel sending request to a apache2 server running on EC2
		print("Parallelising for " + str(Resource) + " EC2 Resources")
		with ThreadPoolExecutor(max_workers=Resource) as executor:
			res_json_table =  executor.map(AskEC2,runs,url_list,js)
		

		
		Var95_Buffer = []
		Var99_Buffer = []
		
		for result in res_json_table:
			Var95_Buffer.append(result['var95'])
			Var99_Buffer.append(result['var99'])
		
		#Data processing using Panda To find the mean of var95 and var99 for each signal over different EC2 results
		var95 = pd.DataFrame(Var95_Buffer)
		var95_mean = var95.mean(axis=0)
		var99 = pd.DataFrame(Var99_Buffer)
		var99_mean = var99.mean(axis=0)
		
		#Output Json 
		res_json ={
			'var95' : var95_mean.tolist(),
			'var99' : var99_mean.tolist(),
			'SHOT' : shots
		}
		elapsed = time.time() - t
		print('Elapsed: ' , elapsed)
		
	else:
		#Using local demo data
		f = open('data_out.json')
		res_json = json.load(f)
	
	#Find Average for var95 and 99
	avg95 = Average(res_json['var95'])
	avg99 = Average(res_json['var99'])
	avg95 = [avg95] * len(res_json['var95'])
	avg99 = [avg99] * len(res_json['var95'])
	

	res_json['shots'] = shots
	Server_shots = res_json['shots']
	#Formatting result table
	resultlist= []
	for i in range(0,len(avg95)):	
		resultlist.append( [ dates[i],round(res_json['var95'][i],4), round(res_json['var99'][i],3) ])

	OutputTuple = {
		'var95' : floatListToString(res_json['var95']),
		'var99' : floatListToString(res_json['var99']),
		'dates' : dates,
		'avg95' : floatListToString(avg95),
		'avg99' : floatListToString(avg99),
		'resultlist' : resultlist,
		'RequestTime' : elapsed,
		'Server_shots' :Server_shots
		}
	return OutputTuple


def clear_audit_log():
	
	s3 = boto3.resource('s3')
	s3object = s3.Object('stonkbucket', 'audit.json')


	filecontent = s3object.get()['Body'].read().decode('utf-8')
	print(filecontent)
	s3object.put(
		Body=(bytes(json.dumps(js_base).encode('UTF-8')))
	)

	filecontent = s3object.get()['Body'].read().decode('utf-8')
	print(filecontent)
	return "cleared"



# Defines a POST supporting calculate route
@app.route('/warmup', methods=['POST'])
def calculateHandler():
	if request.method == 'POST':
		print("Calculate Post")
		global Scale_choice
		Scale_choice = request.form.get('Scale')
		global Resource
		Resource = request.form.get('Resource')
		
		if Scale_choice == '' or Resource =='':
			
			return doRender('index.htm',
			{
				'note' : "Please Input a valid number"
			})
		Resource = int(Resource)
		if Scale_choice == "Lambda":
			runs=[value for value in range(Resource)]

			with ThreadPoolExecutor(max_workers=int(Resource)) as executor:
				init_result = executor.map(PingLambda,runs)

			for result in init_result:
				print(result)

		elif Scale_choice == "EC2":
			ec2 = boto3.resource('ec2', region_name='us-east-1')

			#Request to see numbber of running instances to avoid creating too many instances
			instances = ec2.instances.filter(
			Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
			mylist = [instance for instance in instances] 
			RunningCount = len(mylist)
			
			#Create number of resource depends on the 
			EC2tocreate = Resource - RunningCount
			
			#If we need more resouces
			if EC2tocreate > 0:

				runs=[value for value in range(0,int(EC2tocreate))] #Find the count for runs
				print("Number of resources needs to be create = " + str(EC2tocreate))
				with ThreadPoolExecutor(max_workers=EC2tocreate) as executor:
					init_result = executor.map(create_EC2_resources,runs)
				#TODO EC2 Creation
				for result in init_result:
					print(result)
			else:
				print("Enough EC2 running already")

		return doRender('risk.htm',
		{
			'Resource' : Scale_choice
		})


#Show risk page
@app.route('/risk')
def risk():
	print()
	print("data Loaded")
	global Scale_choice
	Yesno = {}
	return doRender('risk.htm',{
		"Resource" : Scale_choice
	})

#Flask post to calculate risk
@app.route('/RiskCalc', methods=['POST'])
def RiskCalc():
	update_data()
	LengthOfPriceHistory = int(request.form.get('H'))
	
	NumberofDatapoints = int(request.form.get('D'))
	BuyOrSell = request.form.get('T')
	ONLINE_MODE = request.form.get('ONOFF')

	

	print(str(BuyOrSell))
	if LengthOfPriceHistory == '' or NumberofDatapoints == '' or BuyOrSell == '':
		return doRender('risk.htm',
		{'note': 'Please Check input cannot be empty'})

	print("Riskcalc")
	if ONLINE_MODE == "ONLINE":
		print("ONLINE MODE")
		ONLINE_FLAG = True
	elif ONLINE_MODE == "OFFLINE":
		print("OFFLINE MODE")
		ONLINE_FLAG=False
	
	if Scale_choice == "Lambda":
		print("===============================")
		print("=          Lambda             =")
		print("===============================")
		t = time.time()
		OUTPUT = doMonty_lambda(data,LengthOfPriceHistory,NumberofDatapoints,BuyOrSell,ONLINE_FLAG)
		elapsedtime = time.time() - t

	elif Scale_choice == "EC2":
		print("===============================")
		print("=             EC2             =")
		print("===============================")
		t = time.time()
		OUTPUT = doMonty_EC2(data,LengthOfPriceHistory,NumberofDatapoints,BuyOrSell,ONLINE_FLAG)
		elapsedtime = time.time() - t

	#OUtput data format
	data1 = OUTPUT['var95']
	data2 = OUTPUT['var99']
	dates = OUTPUT['dates']
	dates = ' | '.join(dates)
	avg95 = OUTPUT['avg95']
	avg99 = OUTPUT['avg99']
	resultlist =OUTPUT['resultlist']
	Server_shots = OUTPUT['Server_shots']

	
	#### Logging for Audit Page  ######
	audit_json = {
		'Selection (S)' : Scale_choice,
	"Resource (R) " : Resource,
	"Length Of Price History (H)" : LengthOfPriceHistory,
	"Number Of Data shots (D) " : NumberofDatapoints,
	"Buy Or Sell" : BuyOrSell, 
	"Average Var95" : float(avg95.split(',')[0]),
	"Average Var99" : float(avg99.split(',')[0]),
	"Time for Audit" : elapsedtime
	}

	
	#Update Audit JSON 
	s3 = boto3.resource('s3')
	s3object = s3.Object('stonkbucket', 'audit.json')
	filecontent = s3object.get()['Body'].read().decode('utf-8')

	jsoncontent = json.loads(filecontent)
	jsoncontent.append(audit_json) 

	s3object.put(
    Body=(bytes(json.dumps(jsoncontent).encode('UTF-8')))
	)


	print(ONLINE_MODE)
	return doRender('result.htm',
		{'note': ONLINE_MODE+" MODE",
		 'dataVar95': data1,
		 'dataVar99' : data2,
		 'Charts' : 'true',
		 'Dates' : dates,
		 'avg95' : avg95,
		 'avg99' : avg99,
		 'resultlist' : resultlist,
		 'Resource' : Resource,
		 'shots' : Server_shots
		})


@app.route('/cacheavoid/<name>')
def cacheavoid(name):
    # file exists?
    if not os.path.isfile( os.path.join(os.getcwd(), 'static/'+name) ):
        return ( 'No such file ' + os.path.join(os.getcwd(), 'static/'+name) )
    f = open ( os.path.join(os.getcwd(), 'static/'+name) )
    contents = f.read()
    f.close()
    return contents

@app.route('/audit')
def audit():
	s3 = boto3.resource('s3')
	s3object = s3.Object('stonkbucket', 'audit.json')


	filecontent = s3object.get()['Body'].read().decode('utf-8')
	jsonconent = json.loads(filecontent)
	df = pd.DataFrame(jsonconent)
	print(df)
	#print(jsonconent[0]['Select'])	

	return doRender('audit.htm',{
		'data' : df.to_html(classes="table table-bordered table-striped mb-0" , justify="center")
	})


@app.route('/terminateec2')
def terminate_ec2():
	Terminate_EC2()

	return doRender('index.htm',{
		'note' : "ALL EC2 Terminated"
	})



# catch all other page requests - doRender checks if a page is available (shows it) or not (index)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def mainPage(path):
	update_data()

	return doRender(path)
@app.errorhandler(500)




# A small bit of error handling
def server_error(e):
    logging.exception('ERROR!')
    return """
    An  error occurred: <pre>{}</pre>
    """.format(e), 500

if __name__ == '__main__':
    # Entry point for running on the local machine
    # On GAE, endpoints (e.g. /) would be called.
    # Called as: gunicorn -b :$PORT index:app,
    # host is localhost; port is 8080; this file is index (.py)
    app.run(host='127.0.0.1', port=8080, debug=True)
