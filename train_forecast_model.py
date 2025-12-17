
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import datetime

print("Loading ML dataset...")
df = pd.read_csv('dataset_ml_diario.csv')
df['date'] = pd.to_datetime(df['date'])

# ==========================================
# 1. Train / Test Split (Time Series)
# ==========================================
print("Splitting data (Time-based)...")
# Training: 2023 - 2024
# Testing: 2025
train_df = df[df['date'] < '2025-01-01']
test_df = df[df['date'] >= '2025-01-01']

feature_cols = [
    'weather_temp', 'is_weekend', 'is_holiday', 'foot_traffic_estimate',
    'num_reservations', 'reserved_pax',
    'day_of_week', 'month', 'day_of_month',
    'promo_pizza_tuesday', 'promo_ladies_thursday', 'promo_happy_hour',
    'revenue_t-1', 'revenue_t-7', 'revenue_t-28',
    'rolling_7d_avg', 'rolling_30d_avg'
]
target_col = 'target_revenue'

X_train = train_df[feature_cols]
y_train = train_df[target_col]

X_test = test_df[feature_cols]
y_test = test_df[target_col]

print(f"Training Samples: {len(X_train)}")
print(f"Testing Samples: {len(X_test)}")

# ==========================================
# 2. Model Training (Random Forest)
# ==========================================
print("Training Random Forest Regressor...")
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# ==========================================
# 3. Evaluation
# ==========================================
print("Evaluating model...")
train_preds = model.predict(X_train)
test_preds = model.predict(X_test)

# Metrics
test_mae = mean_absolute_error(y_test, test_preds)
test_mape = mean_absolute_percentage_error(y_test, test_preds)
train_mape = mean_absolute_percentage_error(y_train, train_preds)

print("\n" + "="*40)
print("MODEL PERFORMANCE REPORT")
print("="*40)
print(f"Train MAPE: {train_mape:.2%}")
print(f"Test MAPE:  {test_mape:.2%} (Target < 15%)")
print(f"Test MAE:   ${test_mae:,.0f} CLP")

# ==========================================
# 4. Feature Importance
# ==========================================
print("\n" + "="*40)
print("FEATURE IMPORTANCE (Top 10)")
print("="*40)
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]

for i in range(min(10, len(feature_cols))):
    print(f"{i+1}. {feature_cols[indices[i]]:<25} {importances[indices[i]]:.4f}")

# Optional: Simple Prediction for "Tomorrow" (Dummy Example)
print("\n[Simulation] Predicting revenue for a fake 'tomorrow':")
print(f"Input: Thursday, Ladies Night promo, 40 reservations, 25C temp")
# Make a dummy row
dummy_row = X_test.iloc[0].copy()
dummy_row['is_weekend'] = 0
dummy_row['num_reservations'] = 40
dummy_row['weather_temp'] = 25.0
dummy_row['promo_ladies_thursday'] = 1
dummy_row['promo_pizza_tuesday'] = 0

pred_val = model.predict([dummy_row])[0]
print(f"Predicted Revenue: ${pred_val:,.0f} CLP")

print("\n[OK] Model trained and evaluated successfully.")
