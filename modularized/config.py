# config.py
import os

# Configuration settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")
MODEL_DIR = os.path.join(BASE_DIR, "models")
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Model parameters
HYPERPARAMETERS = {
    'classifier__max_depth': [5, 7, 9],
    'classifier__learning_rate': [0.05, 0.1],
    'classifier__subsample': [0.8, 1.0],
    'classifier__colsample_bytree': [0.8, 1.0],
    'classifier__gamma': [0, 0.1, 0.3]
}

# Threshold selection
MIN_PRECISION = 0.60
MIN_RECALL = 0.60

def get_latest_dataset():
    """Get the path to the latest generated dataset"""
    files = os.listdir(DATASET_DIR)
    if not files:
        raise FileNotFoundError("No datasets found")
    return os.path.join(DATASET_DIR, sorted(files, reverse=True)[0])

