from fastapi import HTTPException
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

# loading the trained model
model = joblib.load('best_predictive_maintenance_model.pkl')
scaler = joblib.load('scaler.pkl')

# Data processing and cleaning
def process_data(sensor_data):
    if not sensor_data:
        raise HTTPException(status_code=400, detail="No sensor data available")
    
    df = pd.DataFrame(sensor_data)
    df = df.dropna()  # Remove missing values
    dd = df.drop(['UDI', 'equipment_id'], axis=1)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Train predictive model
def train_model():
    global model
    df = process_data()
    
    # Simulate failure labels (for demonstration purposes)
    df['failure'] = np.random.randint(0, 2, size=len(df))
    
    # Features and target
    X = df[['temperature', 'vibration', 'pressure']]
    y = df['failure']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {accuracy}")
