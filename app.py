<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, abort, url_for, make_response, jsonify
import pymongo
from bson.objectid import ObjectId
import datetime 
import pandas as pd
# Import the function to handle model predictions
from model_handler import get_prediction

app = Flask(__name__)

@app.route('/')
def home():
    """
    Route for the home page
    """
    return render_template("index.html")
    
@app.route('/profile')
def profile():
    """
    Route for the profile page
    """
    return render_template("profile.html")

@app.route('/csvs')
def csvs():
    """
    Route for GET requests to the csvs page
    Shows a user's csvs
    """
    return render_template("csvs.html")

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
    
=======
import os
from flask import Flask, request, jsonify
import pandas as pd
from model_handlers import get_prediction
import pymongo
from dotenv import load_dotenv

app = Flask(__name__)

# Connect to the MongoDB server using environment variables 
load_dotenv()
connection = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = connection[os.getenv('MONGO_DBNAME')]
try:
    # verify the connection works by pinging the database
    connection.admin.command("ping")  
    print(" *", "Connected to MongoDB!")  
except Exception as e:
    # the ping command failed, so the connection is not available.
    print(" * MongoDB connection error:", e)

>>>>>>> c83fc8b0576ea9592d9a862f85fd4edb3f225ed0

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