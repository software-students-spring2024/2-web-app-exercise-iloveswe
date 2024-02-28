import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, abort, url_for, make_response, jsonify, flash
from flask_login import login_user, LoginManager, current_user, login_required, logout_user
import pymongo
from bson.objectid import ObjectId
import datetime 
import pandas as pd
import bcrypt
import pprint
# Import the function to handle model predictions
from model_handler import get_prediction
# import user mode
from User import *

ALLOWED_EXTENSIONS = {'csv'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = b'iloveswe'

login_manager = LoginManager()
login_manager.init_app(app)

# Connect to the MongoDB server using environment variables 
load_dotenv()
connection = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = connection[os.getenv('MONGO_DBNAME')]
users = db.users
try:
    # verify the connection works by pinging the database
    connection.admin.command("ping")  
    print(" *", "Connected to MongoDB!")  
except Exception as e:
    # the ping command failed, so the connection is not available.
    print(" * MongoDB connection error:", e)

@login_manager.user_loader
def load_user(user_id):
    user = User.get_by_id(user_id)
    return user

@app.route('/')
def home():
    """
    Route for the home page
    """
    return render_template("index.html")

@app.route('/register')
def register():
    """
    Route for the user registration page
    """
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register_post():
    """
    Route for the handling POST requests from the registration page
    """
    # get req data
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    #user = users.find_one({"email": email})
    user = User.get_by_email(email)

    if(user):
        # user already exists in db
        flash('Email address already exists')
        return redirect('/register')

    # create new user and add to db
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
    User.register(email, name, hashed_pw)
    pprint.pprint(users.find_one({"email": email}))
    
    return redirect("/login")

@app.route('/login')
def login():
    """
    Route for login
    """   
    return render_template("login.html")  

@app.route('/login', methods=['POST'])
def login_post():
    """
    Route for the handling POST requests from the login page
    """
    # get req data
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    if(not User.login_valid(email, password)):
        flash('Please check your login details and try again')
        return redirect('/login')

    # user login is successful
    user = User.get_by_email(email)
    pprint.pprint(users.find_one({"email": email}))
    res = login_user(user, remember=remember)
    if(res):
        print("Login Successful")
        return redirect("/profile")
    else:
        flash('Please check your login details and try again')
        return redirect('/login')

@app.route('/logout')
@login_required
def logout():
    """
    Route for logging out
    """   
    logout_user()
    return redirect("/") 


@app.route('/profile')
@login_required
def profile():
    """
    Route for the profile page
    """
    return render_template("profile.html", name=current_user.name)

@app.route('/csvs')
def csvs():
    """
    Route for GET requests to the csvs page
    Shows a user's csvs
    """
    return render_template("csvs.html")

@app.route('/csvs', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = file.filename
        print(filename)
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/csvs')

@app.route('/editcsv/<post_id>')
def edit_csv(post_id):
    """
    Route for GET requests to the edit_csv page
    Displays a table of CSV data where users can edit or delete the CSV
    """
    #doc = db.csv.find_one({"_id"} ObjectId(post_id))
    doc = post_id
    return render_template("edit_csv.html", doc=doc)

@app.route('/model/<post_id>')
def model(post_id):
    """
    Route for GET requests to the model page
    Displays the model info
    """
    #doc = db.model.find_one({"_id"} ObjectId(post_id))
    doc = post_id
    return render_template("model.html", doc=doc)
    

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    
    # Validate input data (not shown for brevity)
    
    # Extract relevant information from the request
    model_type = data.get('model_type')
    parameters = data.get('parameters', {})
    stock_data = pd.DataFrame(data['stock_data'])
    
    # Call the model handling function and get the prediction
    try:
        prediction_response = get_prediction(model_type, stock_data, parameters)
        return jsonify({"success": True, "prediction": prediction_response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route('/about')
def about():
    """
    Route for the about page
    """
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)