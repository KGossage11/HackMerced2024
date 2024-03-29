from flask import Flask, jsonify, request, render_template, url_for, redirect, session
from pymongo import MongoClient
import secrets
#####wit
import os
from flask import Flask
from wit import Wit
#####
# Get Wit.ai server access token from environment variable
WIT_AI_ACCESS_TOKEN = "INSERT WIT.AI ACCESS TOKEN HERE"

# Initialize Wit.ai client with your access token
witClient = Wit(WIT_AI_ACCESS_TOKEN)

# Define routes and other Flask application logic here...
#Secret Key is needed for session
secret_key = secrets.token_hex(32)
SECRET_KEY = secret_key

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
client = MongoClient('INSERT MONGODB CLIENT HERE')
# Create a mongodb database
db = client.MyDatabase

# Create a collection - users
user = db.users

# Print Database 
@app.route('/get_data')
def hello_world():
    users = list(user.find({}, {'_id': False}))  # Exclude _id field from results
    # Convert ObjectId to string representation
    for i in users:
        i['_id'] = str(user['_id'])

    return jsonify(users)

# Home Page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the message from the user
        message = request.form['message']
        # Send the message to Wit.ai
        response = witClient.message(message)
        if 'intents' in response and len(response['intents']) > 0:
            # Extract the intent
            wit_response = response['intents'][0]['name']
        else:  # If no intent is detected
            wit_response = 'Sorry, I do not understand.'

        if 'entities' in response and len(response['entities']) > 0:
            # Extract the entities
            entities = response['entities']
        else:
            entities = "None"

        # Return the Wit.ai response
        # return render_template('web.html', response=wit_response, entities=entities)
        return render_template('web.html', response=wit_response, entities=entities)
    return render_template('web.html')

@app.route('/visit', methods=['GET', 'POST'])
def visit():
    if request.method == 'POST':
        # Get the message from the user
        date = request.form['date']
        time = request.form['time']
        reminderOne = request.form['reminderOne']
        reminderTwo = request.form['reminderTwo']
        
        # Get user data from MongoDB
        username = session.get('username')

        userNameData = user.find_one({'users': username})
        if userNameData:
            userNameData['visit'] = {'date': date, 'time': time, 'reminderOne': reminderOne, 'reminderTwo': reminderTwo}
            session['visit'] = "true"
        user.update_one({'users': username}, {'$set': {'visit': userNameData['visit']}})
        return render_template('visits.html', date=date, time=time, reminderOne=reminderOne, reminderTwo=reminderTwo)
    
    username=session.get('username')
    userNameData = user.find_one({'users': username})
    if userNameData and 'visit' in userNameData:
        visit_data = userNameData.get('visit')
        date = visit_data.get('date')
        time = visit_data.get('time')
        reminderOne = visit_data.get('reminderOne')
        reminderTwo = visit_data.get('reminderTwo')
        session['visit'] = "true"
        return render_template('visits.html', date=date, time=time, reminderOne=reminderOne, reminderTwo=reminderTwo)
    else:
        return render_template('visits.html', date="", time="", reminderOne="", reminderTwo="")

@app.route('/services')
def services():
    if 'city' in session:
        return render_template('services.html', city=session['city'])
    return render_template('services.html', city="merced")

@app.route('/profile')
def profile():
    userNameData = session['username']
    cityNameData = session['city']
    emailData = user.find_one({'users': userNameData}).get('email')
    return render_template('profile.html', user = userNameData, email = emailData, city=cityNameData)

@app.route('/logout')
def logout():
    # Remove the everything from the session if it's there
    session.pop('username', None)
    session.pop('password', None)
    session.pop('login', None)
    session.pop('visit', None)
    session.pop('city', None)
    return redirect(url_for('home'))

# Add Data to Database
@app.route('/register', methods=['GET','POST'])
def register(): 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        city = request.form['city']
        user.insert_one({'users': username, 'password': password, 'email': email, 'city': city, 'visit': {}})
        #A session keeps the user logged in for as long as the client is alive
        session['username'] = username
        session['password'] = password
        session['login'] = "true"
        session['city'] = city
        return render_template('web.html', login="true")
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return render_template('login.html', message='Please enter into the fields')
        
        specificUser = user.find_one({'users': username})
        if not specificUser:
            return render_template('login.html', message='User not Found!')
        
        if specificUser['password'] != password:
            return render_template('login.html', message='Password Incorrect!')
        session['username'] = username
        session['password'] = password
        session['login'] = "true"
        session['city'] = specificUser['city']
        return render_template('web.html', login="true")
    
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)

#I broke my leg
#I need a doctor



