# inference.py
import pandas as pd
import numpy as np
import joblib
import os
from .preprocessing import feature_engineering
from .config import MODEL_DIR


class FraudPredictor:
    """Class for making fraud predictions on new data"""
    
    def __init__(self, model_name="fraud_model"):
        """Initialize the predictor by loading model components"""
        self.model_name = model_name
        self.preprocessor = None
        self.classifier = None
        self.threshold = None
        self._load_model_components()
    
    def _load_model_components(self):
        """Load preprocessor, classifier, and threshold"""
        model_dir = MODEL_DIR
        
        # Load preprocessor
        preprocessor_path = os.path.join(model_dir, f"{self.model_name}_preprocessor.joblib")
        self.preprocessor = joblib.load(preprocessor_path)
        
        # Load classifier
        classifier_path = os.path.join(model_dir, f"{self.model_name}_classifier.joblib")
        self.classifier = joblib.load(classifier_path)
        
        # Load threshold
        threshold_path = os.path.join(model_dir, f"{self.model_name}_threshold.txt")
        with open(threshold_path, 'r') as f:
            self.threshold = float(f.read().strip())
        
        print(f"Model components loaded successfully")
        print(f"Using threshold: {self.threshold:.4f}")
    
    def preprocess_data(self, df):
        """Apply feature engineering to new data"""
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Apply same feature engineering as training
        df = feature_engineering(df)
        
        # Select features (same as training)
        features_to_drop = ['is_fraud', 'timestamp', 'customer_id', 'merchant', 'location']
        features_to_drop = [col for col in features_to_drop if col in df.columns]
        X = df.drop(features_to_drop, axis=1)
        
        return X
    
    def predict(self, df, return_proba=False):
        """Make predictions on new data
        
        Args:
            df: DataFrame with transaction data
            return_proba: If True, return probabilities instead of binary predictions
        
        Returns:
            Array of predictions (0/1) or probabilities if return_proba=True
        """
        # Preprocess the data
        X = self.preprocess_data(df.copy())
        
        # Transform using fitted preprocessor
        X_transformed = self.preprocessor.transform(X)
        
        # Get probabilities
        probabilities = self.classifier.predict_proba(X_transformed)[:, 1]
        
        if return_proba:
            return probabilities
        else:
            # Apply threshold
            predictions = (probabilities >= self.threshold).astype(int)
            return predictions
    
    def predict_single(self, transaction_dict):
        """Predict on a single transaction
        
        Args:
            transaction_dict: Dictionary with transaction details
        
        Returns:
            Tuple of (prediction, probability)
        """
        # Convert to DataFrame
        df = pd.DataFrame([transaction_dict])
        
        # Get prediction and probability
        prob = self.predict(df, return_proba=True)[0]
        pred = int(prob >= self.threshold)
        
        return pred, prob


# Example usage function
def example_usage():
    """Example of how to use the FraudPredictor"""
    
    # Initialize predictor
    predictor = FraudPredictor()
    
    # Example 1: Single transaction
    transaction = {
        'amount': 150.0,
        'old_balance': 1000.0,
        'new_balance': 850.0,
        'age': 35,
        'category': 'electronics',
        'gender': 'M',
        'transaction_type': 'purchase',
        'location': 'New York, USA',
        'timestamp': '2024-01-15 14:30:00',
        'customer_id': 'CUST123',
        'merchant': 'Best Electronics'
    }
    
    prediction, probability = predictor.predict_single(transaction)
    print(f"Single transaction prediction: {'Fraud' if prediction else 'Legitimate'}")
    print(f"Fraud probability: {probability:.4f}")
    
    # Example 2: Batch prediction
    # Create sample batch data
    batch_data = pd.DataFrame([
        {
            'amount': 50.0,
            'old_balance': 500.0,
            'new_balance': 450.0,
            'age': 25,
            'category': 'groceries',
            'gender': 'F',
            'transaction_type': 'purchase',
            'location': 'Los Angeles, USA',
            'timestamp': '2024-01-15 10:00:00',
            'customer_id': 'CUST456',
            'merchant': 'Super Market'
        },
        {
            'amount': 2000.0,
            'old_balance': 1500.0,
            'new_balance': -500.0,
            'age': 45,
            'category': 'travel',
            'gender': 'M',
            'transaction_type': 'withdrawal',
            'location': 'Miami, USA',
            'timestamp': '2024-01-15 23:45:00',
            'customer_id': 'CUST789',
            'merchant': 'ATM'
        }
    ])
    
    predictions = predictor.predict(batch_data)
    probabilities = predictor.predict(batch_data, return_proba=True)
    
    print("\nBatch predictions:")
    for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
        print(f"Transaction {i+1}: {'Fraud' if pred else 'Legitimate'} (probability: {prob:.4f})")


if __name__ == "__main__":
    example_usage()

    