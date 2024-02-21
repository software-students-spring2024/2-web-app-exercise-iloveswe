from flask import Flask, request, jsonify
import pandas as pd
# Import the function to handle model predictions
from model_handlers import get_prediction

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
