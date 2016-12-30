# Run Script
import os
os.system("musicapp.py 1")

# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, request, url_for

# Initialize the Flask application
app = Flask(__name__)

# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    return render_template('index.html')

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is 
# accepting: POST requests in this case
@app.route('/hello/', methods=['POST'])
def hello():
    from musicapp import get_data2
    name=request.form['bandname']
    return render_template('submit.html', name=name, answer=get_data2(name))

# Run the app :)
if __name__ == '__main__':
  app.run()