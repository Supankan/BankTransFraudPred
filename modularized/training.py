# training.py
import joblib
import numpy as np
import os
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from config import MODEL_DIR, HYPERPARAMETERS, RANDOM_STATE
from preprocessing import get_preprocessor
from sklearn.metrics import precision_recall_curve, f1_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline


def train_model(X_train, y_train):
    """Train model with SMOTE and hyperparameter tuning"""
    preprocessor = get_preprocessor()
    
    # Create pipeline with SMOTE and XGBoost
    pipeline = ImbPipeline(steps=[
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=RANDOM_STATE)),
        ('classifier', XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ])
    
    # Hyperparameter tuning
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    grid_search = GridSearchCV(
        pipeline, 
        HYPERPARAMETERS, 
        cv=cv, 
        scoring='f1',  # Optimize for F1 score
        n_jobs=-1,
        verbose=1
    )
    
    print("Starting model training with SMOTE...")
    grid_search.fit(X_train, y_train)
    print("Training complete!")
    
    best_model = grid_search.best_estimator_
    best_params = grid_search.best_params_
    best_score = grid_search.best_score_
    
    print(f"Best parameters: {best_params}")
    print(f"Best F1 score (CV): {best_score:.4f}")
    
    return best_model

def find_optimal_threshold(model, X, y_true, min_precision=0.60, min_recall=0.60):
    """Find optimal threshold meeting precision/recall requirements"""
    # Get predicted probabilities
    y_proba = model.predict_proba(X)[:, 1]
    
    # Calculate precision-recall curve
    precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
    
    # Find thresholds that meet minimum requirements
    candidate_thresholds = []
    for i, thresh in enumerate(thresholds):
        if precision[i] >= min_precision and recall[i] >= min_recall:
            candidate_thresholds.append((thresh, f1_score(y_true, y_proba >= thresh)))
    
    # Select best threshold
    if candidate_thresholds:
        # Sort by F1 score (descending)
        candidate_thresholds.sort(key=lambda x: x[1], reverse=True)
        best_threshold, best_f1 = candidate_thresholds[0]
        print(f"Found threshold meeting requirements: {best_threshold:.4f} (F1={best_f1:.4f})")
    else:
        # If no threshold meets both, find one that maximizes F1
        print("No threshold meets both min precision and recall requirements.")
        print("Selecting threshold that maximizes F1 score.")
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-9)
        best_idx = np.argmax(f1_scores)
        best_threshold = thresholds[best_idx]
        best_f1 = f1_scores[best_idx]
        print(f"Best F1 threshold: {best_threshold:.4f} (F1={best_f1:.4f})")
    
    return best_threshold

def save_model(model, threshold, model_name="fraud_model"):
    """Save model pipeline and threshold to disk"""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Save the entire pipeline (includes preprocessor + SMOTE + classifier)
    pipeline_path = os.path.join(MODEL_DIR, f"{model_name}_pipeline.joblib")
    joblib.dump(model, pipeline_path)
    
    # Also save just the preprocessor for inference (without SMOTE)
    preprocessor = model.named_steps['preprocessor']
    preprocessor_path = os.path.join(MODEL_DIR, f"{model_name}_preprocessor.joblib")
    joblib.dump(preprocessor, preprocessor_path)
    
    # Save the classifier separately for cases where you might want it
    classifier = model.named_steps['classifier']
    classifier_path = os.path.join(MODEL_DIR, f"{model_name}_classifier.joblib")
    joblib.dump(classifier, classifier_path)
    
    # Save threshold
    threshold_path = os.path.join(MODEL_DIR, f"{model_name}_threshold.txt")
    with open(threshold_path, 'w') as f:
        f.write(str(threshold))
    
    print(f"Full pipeline saved to {pipeline_path}")
    print(f"Preprocessor saved to {preprocessor_path}")
    print(f"Classifier saved to {classifier_path}")
    print(f"Threshold saved to {threshold_path}")
    
    return pipeline_path, preprocessor_path, classifier_path, threshold_path

def load_model_for_inference(model_name="fraud_model"):
    """Load model components for inference"""
    model_dir = MODEL_DIR
    
    # Load preprocessor
    preprocessor_path = os.path.join(model_dir, f"{model_name}_preprocessor.joblib")
    preprocessor = joblib.load(preprocessor_path)
    
    # Load classifier
    classifier_path = os.path.join(model_dir, f"{model_name}_classifier.joblib")
    classifier = joblib.load(classifier_path)
    
    # Load threshold
    threshold_path = os.path.join(model_dir, f"{model_name}_threshold.txt")
    with open(threshold_path, 'r') as f:
        threshold = float(f.read().strip())
    
    return preprocessor, classifier, threshold

