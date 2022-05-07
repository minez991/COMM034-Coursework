import os
import logging

from flask import Flask, request, render_template

app = Flask(__name__)

#Pikachu list
Pokemons =["Pikachu", "Charizard", "Squirtle", "Jigglypuff", 
           "Bulbasaur", "Gengar", "Charmander", "Mew", "Lugia"]



#Abstraction of code to create amazon_scaleable instances
def Create 



# various Flask explanations available at:  https://flask.palletsprojects.com/en/1.1.x/quickstart/

def doRender(tname, values={}):
	if not os.path.isfile( os.path.join(os.getcwd(), 'templates/'+tname) ): #No such file
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
		l = request.form.get('labour')
		c = request.form.get('conservative')
		test_2 = request.form.get('conservative_2')
		print(str(test_2))
		if l == '' or c == '':
			return doRender('index.htm',
					{'note': 'Please specify a number for each group!'})
		else:
			total = float(l) + float(c)
			lP = int(float(l)/total*100)
			cP = int(float(c)/total*100)
			test2 = int(float(test_2)/total*100)
			return doRender('chart.htm', {'data': str(lP) + ',' + str(cP)+','+str(test2)})
	return 'Should not ever get here'


@app.route('/table')
def table():
	return render_template('table.htm',len = len(Pokemons), Pokemons = Pokemons)

@app.route('/random', methods=['POST'])
def RandomHandler():
	import http.client
	if request.method == 'POST':
		v = request.form.get('key1')
		c = http.client.HTTPSConnection("cms03i6rod.execute-api.us-east-1.amazonaws.com")
		json= '{ "key1": "'+v+'"}'
		c.request("POST", "/default/function_one", json)
		response = c.getresponse()
		data = response.read().decode('utf-8')
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
