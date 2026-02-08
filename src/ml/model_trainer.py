import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def train_model(dataset_path="training_dataset.parquet", model_output="weather_risk_model.pkl"):
    print(f"--- Loading Dataset: {dataset_path} ---")
    try:
        df = pd.read_parquet(dataset_path)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns}")
    
    # Feature Engineering / Selection
    # We want to predict 'target_risk' (Any risk)
    # Features: 10u, 10v, 2t, latitude, longitude
    # Note: Column names might vary if renaming wasn't perfect, let's check
    
    feature_cols = ['10u', '10v', '2t', 'latitude', 'longitude']
    
    # Check if columns exist
    missing_cols = [c for c in feature_cols if c not in df.columns]
    if missing_cols:
        print(f"Missing feature columns: {missing_cols}")
        print("Available columns:", df.columns)
        # Fallback logic if needed, or return
        return

    X = df[feature_cols]
    y = df['target_risk']
    
    print("Features sample:")
    print(X.head())
    
    # Train/Test Split
    print("Splitting Data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model Training
    print("Training Random Forest Classifier...")
    # Using limited depth and estimators for speed in prototype
    clf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    
    # Evaluation
    print("Evaluating Model...")
    y_pred = clf.predict(X_test)
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Interaction: Feature Importance
    importances = clf.feature_importances_
    feat_importance = pd.DataFrame({'feature': feature_cols, 'importance': importances})
    print("\nFeature Importance:")
    print(feat_importance.sort_values(by='importance', ascending=False))
    
    # Save Model
    joblib.dump(clf, model_output)
    print(f"\nModel saved to {model_output}")

if __name__ == "__main__":
    train_model()
