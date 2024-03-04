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

app = Flask(__name__)
app.secret_key = b'iloveswe'

login_manager = LoginManager()
login_manager.init_app(app)

# Connect to the MongoDB server using environment variables 
load_dotenv()
connection = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = connection[os.getenv('MONGO_DBNAME')]
users = db.users
strategies_docs = db.strategies
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

@login_manager.unauthorized_handler 
def unauthorized_callback():
    return redirect(url_for('login'))

@app.route('/')
@login_required
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
        return redirect("/")
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

@app.route('/strategies')
@login_required
def strategies():
    """
    Route for GET requests to the strategies page
    Shows a user's strategies
    """
    user_email = current_user.email
    user = db.users.find_one({"email": user_email})
    strats = []
    try:
        strategy_ids = user["strategies"]
        for e in strategy_ids:
            strat = db.strategies.find_one({"_id": e})
            strats.append(strat)
    except:
        print('No strats')
    return render_template("strategies.html", strategies = strats)

@app.route('/strategy/<strat_id>')
@login_required
def strategy(strat_id):
    """
    Route for GET requests to a strategy page
    """
    strat = db.strategies.find_one({"_id": ObjectId(strat_id)})
    print(strat)
    return render_template("strategy.html", strat=strat)

@app.route('/edit-strategy/<strat_id>')
@login_required
def edit_strategy(strat_id):
    """
    Route for GET requests to an edit-strategy page
    """
    #doc = db.csv.find_one({"_id"} ObjectId(post_id))
    strat = db.strategies.find_one({"_id": ObjectId(strat_id)})
    return render_template("edit_strategy.html", strat=strat)

@app.route('/edit-strategy/<strat_id>', methods=['POST'])
@login_required
def edit_strategy_post(strat_id):
    """
    Route for POST requests to a strategy page
    """
    # get req data
    strat_name = request.form.get('strategy-name')
    buy = request.form.get('buy')
    hold = request.form.get('hold')
    sell = request.form.get('sell')
    print(strat_name,buy,hold,sell)
    # update fields
    strat = db.strategies.find_one({"_id": ObjectId(strat_id)})
    strat["name"] = strat_name
    strat["buy"] = buy
    strat["hold"] = hold
    strat["sell"] = sell
    # replace in db
    result = db.strategies.replace_one({"_id": ObjectId(strat_id)}, strat)
    print(result)
    flash(f"{strat['name']} edited")
    return redirect("/strategy/"+strat_id)

@app.route('/delete-strategy/<strat_id>', methods=['POST'])
@login_required
def delete_strategy(strat_id):
    """
    Route for POST requests to delete a strategy
    """
    strat = db.strategies.find_one({"_id": ObjectId(strat_id)})
    name = strat["name"]
    # get strat from database
    r = db.strategies.delete_one({"_id": ObjectId(strat_id)})
    print(r)
    flash(f"{name} Deleted")
    return redirect("/strategies")

@app.route('/model/<model_id>')
@login_required
def model(model_id):
    """
    Route for GET requests to the model page
    Displays the model info
    """
    logo_urls = {
        "amazon": "logos/amazon.png",
        "apple": "logos/apple.png",
        "google": "logos/google.png",
        "meta": "logos/meta.png",
        "nvda": "logos/nvda.png"
    }
    graph_urls = {
        "amazon": "graphs/AMZNmodelvsActual.png",
        "apple": "graphs/apple_modelpredVSactual.png",
        "google": "graphs/GOOGLEModelVsActual.png",
        "meta": "graphs/METAModelvsActual.png",
        "nvda": "graphs/nvdamodelvsactual.png"
    }
    logo_url = logo_urls[model_id]
    graph_url = graph_urls[model_id]
    doc = {"logo": logo_url, "graph": graph_url, "model": model_id}
    df = pd.read_csv(f"./data/predictions/{model_id}.csv")
    return render_template("model.html", doc=doc, tables=[df.to_html(classes=["table-bordered", "table-striped", "table-hover", "table"])], titles=df.columns.values)
    

@app.route('/model/<model_id>', methods=['POST'])
@login_required
def model_post(model_id):
    """
    Route for POST requests to the model page
    """
    # get req data
    strat_name = request.form.get('strategy-name')
    buy = request.form.get('buy')
    hold = request.form.get('hold')
    sell = request.form.get('sell')
    strategy = {"name": strat_name, "buy": buy, "hold": hold, "sell": sell}
    print(strat_name,buy,hold,sell)
    #doc = db.model.find_one({"_id"} ObjectId(post_id))
    doc = model_id

    strategy_id = strategies_docs.insert_one(strategy).inserted_id
    user_email = current_user.email
    user = db.users.find_one({"email": user_email})
    print(user)
    try:
        user["strategies"].append(strategy_id)
        result = users.update_one({"_id": user["_id"]}, {"$set": {"strategies": user["strategies"]}})
        print(result)
    except:
        user["strategies"] = [strategy_id]
        result = users.update_one({"_id": user["_id"]}, {"$set": {"strategies": user["strategies"]}})
        print(result)

    flash("Strategy Created")
    return redirect("/model/"+model_id)

@app.route('/about')
def about():
    """
    Route for the about page
    """
    return render_template("about.html")

# route to handle any errors
@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors
    """
    return render_template("error.html", error=e)


if __name__ == '__main__':
    app.run(debug=True)