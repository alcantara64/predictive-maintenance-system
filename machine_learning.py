from fastapi import HTTPException
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

# loading the trained model
model = joblib.load('best_model.pkl')
scaler = joblib.load('scaler.pkl')

# Data processing and cleaning
def process_data(sensor_data):
    if not sensor_data:
        raise HTTPException(status_code=400, detail="No sensor data available")
    
    df = pd.DataFrame(sensor_data)
    df = df.dropna()  # Remove missing values
    dd = df.drop(['device', 'equipment_id'], axis=1)
    return df

# Train predictive model
def train_model():
    global trained_model
    df = process_data()
    
    # Features and target
    X = df[['metric1', 'metric1', 'metric2','metric3', 'metric4','metric5','metric6','metric7','metric8','metric9',]]
    y = df['failure']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    trained_model = RandomForestClassifier()
    trained_model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = trained_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {accuracy}")
