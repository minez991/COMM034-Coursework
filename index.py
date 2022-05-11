from crypt import methods
from doctest import OutputChecker
import os
import logging
import math
import random
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from pandas_datareader import data as pdr
import json
from flask import Flask, request, render_template
import time

app = Flask(__name__)
#####################################################
## Not the most pythonic method, but debug toggles ##
#####################################################

# Toggle True if uses local data store in static, this is used for front end debug, to reduce time and computation cost


#Pikachu list
Pokemons =["Pikachu", "Charizard", "Squirtle", "Jigglypuff", 
           "Bulbasaur", "Gengar", "Charmander", "Mew", "Lugia"]

os.environ['AWS_SHARED_CREDENTIALS_FILE']='./static/cred'
import boto3


### AWS Setup
AWS_S3_BUCKET = 's3://stonkbucket'




#Local Test function for front end of the webpage.
def doMonty(data,minhistory = 101,shots= 80000,BuyorSellOption="Buy",ONLINE_MODE = False):
	import http.client
	minhistory = 101
	shots = 80000
	var95_table = []
	var99_table = []
	#ONLINE_MODE = False

	shots=int(shots)
	#print("buy or sell ",BuyorSellOption + "\n\n")
	mean = []
	std = []
	if BuyorSellOption == "Buy":
		print("Client wants to buy")
		#calculate all data to find the mean and std of data
		for i in range(minhistory, len(data)): 
			if data.Buy[i]==1: # if we were only interested in Buy signals
					mean.append(data.Close[i-minhistory:i].pct_change(1).mean())
					std.append(data.Close[i-minhistory:i].pct_change(1).std())

	elif BuyorSellOption == "Sell":
		print("Client wants to Sell")
		for i in range(minhistory, len(data)): 
			if data.Sell[i]==1: # if we were only interested in Buy signals
					mean.append(data.Close[i-minhistory:i].pct_change(1).mean())
					std.append(data.Close[i-minhistory:i].pct_change(1).std())
	js = {
		'mean' : mean,
		'std' : std,
		'shots' : shots
	}


	js = json.dumps(js)
	#If we are not using local data
	if ONLINE_MODE:
		t = time.time()
		client = boto3.client('lambda', region_name='us-east-1')
		response = client.invoke(
		# use your own ARN below
		FunctionName='arn:aws:lambda:us-east-1:564060094405:function:ReturnVarAvg',
		InvocationType='RequestResponse',
		LogType='None',
		Payload=js
		)
		# Ways of working with the response
		#print(response)
		#print(response['Payload'])
		r=response['Payload'].read()
		res_json = json.loads(r) # sometimes, it is necessary to use .decode("utf-8"))
		
		#with open('data_out.json', 'w') as f:
		#	json.dump(res_json, f)
		elapsed = time.time() - t
		print('Elapsed: %s' , elapsed)

	else:
		f = open('data_out.json')
		res_json = json.load(f)
	print(type(res_json['var95']))

	OutputTuple = (floatListToString(res_json['var95']),floatListToString(res_json['var99']))

	#print(floatListToString(var95_table))
	#OutputTuple = (floatListToString(var95_table),floatListToString(var99_table))


	return OutputTuple

def floatListToString(floatList):
	OutputString = ''
	for num in floatList[:-1]:
		OutputString = OutputString + str(num) + ','
	OutputString = OutputString + str(floatList[-1])
	return OutputString
#Abstraction of code to create amazon_scaleable instances


# various Flask explanations available at:  https://flask.palletsprojects.com/en/1.1.x/quickstart/

def doRender(tname, values={}):
	if not (os.path.isfile( os.path.join(os.getcwd(), 'templates/'+tname)) ): #No such file
		print("No File")
		return render_template('index.htm')
	return render_template(tname, **values)

@app.route('/hello')
# Keep a Hello World message to show that at least something is working
def hello():
    return 'Hello World!'


# Defines a POST supporting calculate route
@app.route('/calculate', methods=['POST'])
def calculateHandler():
	if request.method == 'POST':
		print("Calculate Post")
		l = request.form.get('Scale')
		print(l)
		c = request.form.get('Resource')
		if l == '' or c == '':
			return doRender('index.htm',
					{'note': 'Please specify a number for each group!'})
		else:
			total = float(l) + float(c)
			lP = int(float(l)/total*100)
			cP = int(float(c)/total*100)
			return doRender('chart.htm', {'data': str(lP) + ',' + str(cP)})
	return 'Should not ever get here'


@app.route('/table')
def table():
	return render_template('table.htm',len = len(Pokemons), Pokemons = Pokemons)


@app.route('/risk')
def risk():
	print()
	print("data Loaded")
	Yesno = {}
	return render_template('risk.htm')

@app.route('/RiskCalc', methods=['POST'])
def RiskCalc():

	LengthOfPriceHistory = request.form.get('H')
	NumberofDatapoints = request.form.get('D')
	BuyOrSell = request.form.get('T')
	ONLINE_MODE = request.form.get('ONOFF')

	print(str(BuyOrSell))
	if LengthOfPriceHistory == '' or NumberofDatapoints == '' or BuyOrSell == '':
		return doRender('risk.htm',
		{'note': 'Please Check input cannot be empty'})

	# Code from the python script provided in coursework document, get data here
	yf.pdr_override()


	# Get stock data from Yahoo Finance – here, asking for about 10 years of Gamestop
	# which had an interesting time in 2021: https://en.wikipedia.org/wiki/GameStop_short_squeeze 
	today = date.today()
	decadeAgo = today - timedelta(days=3652)

	#Date| Open| High| Low | Close | adj close |Volumn | 
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
			#print("S", data.Open[i], data.High[i], data.Low[i], data.Close[i])

	if BuyOrSell == "Buy":
		Selected_data = data.loc[data['Buy'] ==1]
	elif BuyOrSell == "Sell":
		Selected_data = data.loc[data['Sell'] ==1]
	print("Riskcalc")
	if ONLINE_MODE == "ONLINE":
		print("ONLINE MODE")
		ONLINE_FLAG = True
	elif ONLINE_MODE == "OFFLINE":
		print("OFFLINE MODE")
		ONLINE_FLAG=False

	OUTPUT = doMonty(data,LengthOfPriceHistory,NumberofDatapoints,BuyOrSell,ONLINE_FLAG)
	#print(OUTPUT[0])
	data1 = OUTPUT[0]
	data2 = OUTPUT[1]
	#data1 = "-0.054,-0.054,-0.052,-0.047"

	print(ONLINE_MODE)
	return doRender('risk.htm',
		{'note': ONLINE_MODE+" MODE",
		 'dataVar95': data1,
		 'dataVar99' : data2,
		 'Charts' : 'true'
		})

@app.route('/random', methods=['POST'])
def RandomHandler():
	import http.client
	if request.method == 'POST':
		v = request.form.get('key1')
		c = http.client.HTTPSConnection("24vn514n19.execute-api.us-east-1.amazonaws.com")
		json= '{ "key1": "'+v+'"}'
		c.request("POST", "/default/ReturnVarAvg", json)
		response = c.getresponse()
		data = response.read().decode('utf-8')
		print(data)
		return doRender( 'index.htm',
			{'note': data})
		

@app.route('/cacheavoid/<name>')
def cacheavoid(name):
    # file exists?
    if not os.path.isfile( os.path.join(os.getcwd(), 'static/'+name) ):
        return ( 'No such file ' + os.path.join(os.getcwd(), 'static/'+name) )
    f = open ( os.path.join(os.getcwd(), 'static/'+name) )
    contents = f.read()
    f.close()
    return contents

@app.route('/s3')
def s3listbuckets():
    os.environ['AWS_SHARED_CREDENTIALS_FILE']='./cred'
    # Above line needs to be here before boto3 to ensure file is read
    import boto3

    s3 = boto3.resource('s3')
    bucketnames=[bucket.name for bucket in s3.buckets.all()]
    return doRender('index.htm', {'note': ' '.join(bucketnames)})



# catch all other page requests - doRender checks if a page is available (shows it) or not (index)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def mainPage(path):


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
