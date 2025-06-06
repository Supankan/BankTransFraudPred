# api_example.py
from flask import Flask, request, jsonify
from modularized.inference import FraudPredictor
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Initialize the fraud predictor once when the server starts
predictor = FraudPredictor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/predict', methods=['POST'])
def predict():
    """Predict fraud for a single transaction"""
    try:
        # Get transaction data from request
        transaction = request.json
        
        # Validate required fields
        required_fields = [
            'amount', 'old_balance', 'new_balance', 'age', 
            'category', 'gender', 'transaction_type', 'location'
        ]
        
        missing_fields = [field for field in required_fields if field not in transaction]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {missing_fields}'
            }), 400
        
        # Add timestamp if not provided
        if 'timestamp' not in transaction:
            transaction['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add default values for optional fields
        if 'customer_id' not in transaction:
            transaction['customer_id'] = 'UNKNOWN'
        if 'merchant' not in transaction:
            transaction['merchant'] = 'UNKNOWN'
        
        # Make prediction
        prediction, probability = predictor.predict_single(transaction)
        
        # Prepare response
        response = {
            'is_fraud': bool(prediction),
            'fraud_probability': float(probability),
            'threshold': float(predictor.threshold),
            'risk_level': 'HIGH' if probability > 0.8 else 'MEDIUM' if probability > 0.5 else 'LOW'
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    """Predict fraud for multiple transactions"""
    try:
        # Get transactions data from request
        data = request.json
        
        if 'transactions' not in data:
            return jsonify({'error': 'Missing transactions field'}), 400
        
        transactions = data['transactions']
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Add timestamps if not provided
        if 'timestamp' not in df.columns:
            df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add default values for optional fields
        if 'customer_id' not in df.columns:
            df['customer_id'] = 'UNKNOWN'
        if 'merchant' not in df.columns:
            df['merchant'] = 'UNKNOWN'
        
        # Make predictions
        predictions = predictor.predict(df)
        probabilities = predictor.predict(df, return_proba=True)
        
        # Prepare response
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            results.append({
                'transaction_index': i,
                'is_fraud': bool(pred),
                'fraud_probability': float(prob),
                'risk_level': 'HIGH' if prob > 0.8 else 'MEDIUM' if prob > 0.5 else 'LOW'
            })
        
        response = {
            'threshold': float(predictor.threshold),
            'total_transactions': len(results),
            'fraud_count': int(sum(predictions)),
            'results': results
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Example curl commands for testing:
"""
# Single prediction:
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.0,
    "old_balance": 1000.0,
    "new_balance": 500.0,
    "age": 35,
    "category": "electronics",
    "gender": "M",
    "transaction_type": "purchase",
    "location": "New York, USA"
  }'

# Batch prediction:
curl -X POST http://localhost:5000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {
        "amount": 50.0,
        "old_balance": 500.0,
        "new_balance": 450.0,
        "age": 25,
        "category": "groceries",
        "gender": "F",
        "transaction_type": "purchase",
        "location": "Los Angeles, USA"
      },
      {
        "amount": 2000.0,
        "old_balance": 1500.0,
        "new_balance": -500.0,
        "age": 45,
        "category": "travel",
        "gender": "M",
        "transaction_type": "withdrawal",
        "location": "Miami, USA"
      }
    ]
  }'
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

