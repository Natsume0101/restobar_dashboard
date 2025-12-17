
import pandas as pd
import numpy as np
import json
from datetime import timedelta

print("Loading raw datasets...")
# Load Promos
with open('promociones_reales.json', 'r', encoding='utf-8') as f:
    PROMOS = json.load(f)

# Load Sales
sales_df = pd.read_csv('ventas_sinteticas_3anos.csv')
sales_df['date'] = pd.to_datetime(sales_df['date'])

# Load Reservations
reservas_df = pd.read_csv('reservas.csv')
reservas_df['date'] = pd.to_datetime(reservas_df['date'])

print("Aggregating daily metrics...")
# 1. Daily Sales Target (Revenue) & Weather
daily_sales = sales_df.groupby('date').agg({
    'revenue': 'sum',
    'qty_sold': 'sum',
    'weather_temp': 'max', # Assuming max temp for day
    'is_weekend': 'max',
    'is_holiday': 'max',
    'foot_traffic_estimate': 'mean' # Average estimate
}).reset_index()

daily_sales.rename(columns={'revenue': 'target_revenue'}, inplace=True)

# 2. Daily Reservations Features
# Count total reservations and total pax reserved per day
daily_res = reservas_df.groupby('date').agg({
    'reservation_id': 'count',
    'pax': 'sum'
}).rename(columns={'reservation_id': 'num_reservations', 'pax': 'reserved_pax'}).reset_index()

# Merge Sales + Reservations
# Left join to keep all sales days (even if 0 reservations)
ml_df = pd.merge(daily_sales, daily_res, on='date', how='left')
ml_df.fillna({'num_reservations': 0, 'reserved_pax': 0}, inplace=True)

# 3. Calendar & Promo Features
print("Engineering calendar and promo features...")
ml_df['day_of_week'] = ml_df['date'].dt.dayofweek
ml_df['month'] = ml_df['date'].dt.month
ml_df['day_of_month'] = ml_df['date'].dt.day
ml_df['is_weekend'] = ml_df['is_weekend'].astype(int)
ml_df['is_holiday'] = ml_df['is_holiday'].astype(int)

# One-Hot Encode Specific Promos (Simplified)
# We know specific days correlate with promos
ml_df['promo_pizza_tuesday'] = (ml_df['day_of_week'] == 1).astype(int)
ml_df['promo_ladies_thursday'] = (ml_df['day_of_week'] == 3).astype(int)
ml_df['promo_happy_hour'] = ((ml_df['day_of_week'] < 5) & (ml_df['is_holiday'] == 0)).astype(int) # Mon-Fri

# 4. Lag Features (Time Series specific)
print("Creating lag features...")
# Shift revenue to simulate "knowing the past"
# Lag 1: Revenue Yesterday
# Lag 7: Revenue Same Day Last Week
# Lag 28: Revenue Same Day Last Month (approx)

ml_df.sort_values('date', inplace=True)

ml_df['revenue_t-1'] = ml_df['target_revenue'].shift(1)
ml_df['revenue_t-7'] = ml_df['target_revenue'].shift(7)
ml_df['revenue_t-28'] = ml_df['target_revenue'].shift(28)

# Rolling Averages (Trend)
ml_df['rolling_7d_avg'] = ml_df['target_revenue'].shift(1).rolling(window=7).mean()
ml_df['rolling_30d_avg'] = ml_df['target_revenue'].shift(1).rolling(window=30).mean()

# Drop rows with NaNs created by lags (first month approx)
ml_df_clean = ml_df.dropna()

print(f"Final Dataset Shape: {ml_df_clean.shape}")
print(ml_df_clean.head())

ml_df_clean.to_csv('dataset_ml_diario.csv', index=False)
print("[OK] Generated 'dataset_ml_diario.csv' ready for training.")
