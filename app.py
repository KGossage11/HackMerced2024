from flask import Flask, jsonify, request, render_template, url_for, redirect, session
from pymongo import MongoClient
import secrets
secret_key = secrets.token_hex(32)
SECRET_KEY = secret_key

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
client = MongoClient('mongodb+srv://admin:Password@ucmhackathon2024.gxlbdrt.mongodb.net/?retryWrites=true&w=majority&appName=UCMHackathon2024')
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
@app.route('/')
def home():
    return render_template('web.html')

@app.route('/visit')
def visit():
    return render_template('visits.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/medical')
def medical():
    return render_template('medical.html')


# Add Data to Database
@app.route('/register', methods=['GET','POST'])
def register(): 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user.insert_one({'users': username, 'password': password, 'email': email})
        session['username'] = username
        session['password'] = password
        return render_template('register.html', message='User added!')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        print(session['username'])
        return render_template('web.html')

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
        return render_template('web.html', login="true")
    
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)