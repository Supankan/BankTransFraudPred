# preprocessing.py
import pandas as pd
import numpy as np
from .config import get_latest_dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

def load_and_preprocess_data():
    """Load and preprocess the latest dataset"""
    # Load data
    data_path = get_latest_dataset()
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Feature engineering
    df = feature_engineering(df)
    
    # Split features and target
    X = df.drop(['is_fraud', 'timestamp', 'customer_id', 'merchant', 'location'], axis=1)
    y = df['is_fraud']
    
    return X, y

def feature_engineering(df):
    """Create additional features"""
    # Time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    
    # Balance features
    df['balance_diff'] = df['old_balance'] - df['new_balance']
    df['overdraft_attempt'] = np.where(df['amount'] > df['old_balance'], 1, 0)
    df['amount_to_balance_ratio'] = df['amount'] / (df['old_balance'] + 1e-6)
    
    # Risk flags
    df['is_night'] = df['hour'].apply(lambda x: 1 if x < 5 or x > 22 else 0)
    df['is_high_risk_category'] = df['category'].isin(['electronics', 'travel', 'gaming']).astype(int)
    
    # Country extraction
    df['country'] = df['location'].str.split(',').str[-1].str.strip()
    
    return df

def get_preprocessor():
    """Create preprocessing pipeline"""
    numeric_features = ['amount', 'old_balance', 'new_balance', 'age', 'hour', 
                       'day_of_week', 'balance_diff', 'amount_to_balance_ratio']
    categorical_features = ['category', 'gender', 'transaction_type', 'country']
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
    
    return ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)])

