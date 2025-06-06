# evaluation.py
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, 
    ConfusionMatrixDisplay, average_precision_score,
    RocCurveDisplay, PrecisionRecallDisplay
)

def evaluate_model(model, threshold, X_test, y_test):
    """Evaluate model performance with given threshold"""
    # Predict probabilities
    y_proba = model.predict_proba(X_test)[:, 1]
    
    # Apply threshold
    y_pred = (y_proba >= threshold).astype(int)
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_proba),
        'pr_auc': average_precision_score(y_test, y_proba)
    }
    
    # Print metrics
    print("Model Evaluation Metrics:")
    for name, value in metrics.items():
        print(f"{name.capitalize()}: {value:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Legit', 'Fraud'], 
                yticklabels=['Legit', 'Fraud'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()
    
    # ROC curve
    RocCurveDisplay.from_predictions(y_test, y_proba)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.title('ROC Curve')
    plt.show()
    
    # Precision-Recall curve
    PrecisionRecallDisplay.from_predictions(y_test, y_proba)
    plt.title('Precision-Recall Curve')
    plt.show()
    
    return metrics

