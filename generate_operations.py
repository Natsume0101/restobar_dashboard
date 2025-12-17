
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

# ==========================================
# CONFIGURATION
# ==========================================
print("Loading configurations and sales data...")
# Load Promos to know which days to skip for reservations
with open('promociones_reales.json', 'r', encoding='utf-8') as f:
    PROMOS = json.load(f)

# Load Sales to correlate data
sales_df = pd.read_csv('ventas_sinteticas_3anos.csv')
sales_df['date'] = pd.to_datetime(sales_df['date'])

# Group sales by day to get daily stats
daily_stats = sales_df.groupby('date').agg({
    'qty_sold': 'sum',
    'revenue': 'sum',
    'foot_traffic_estimate': 'max', # This was generated in sales script
    'day_of_week': 'max'
}).reset_index()

# ==========================================
# 1. STAFFING (RRHH / TURNOS)
# ==========================================
print("Generating Staffing (RRHH) data...")
staff_log = []

# Roles and Costs (Hourly)
ROLES = {
    'Garzon': {'cost': 3500, 'capacity': 25}, # 1 waiter per 25 items/covers
    'Cocinero': {'cost': 4500, 'capacity': 35}, # 1 cook per 35 items
    'Bartender': {'cost': 4000, 'capacity': 50}, # 1 barman per 50 drinks? (simplified to total items)
    'Admin': {'cost': 6000, 'fixed': 1} # Always 1 admin
}

for _, row in daily_stats.iterrows():
    date = row['date']
    items_sold = row['qty_sold']
    # Approximation: 1 item ~= 1 "effort unit". 
    # Realistically covers = items / 2.5, but let's map directly to capacity for simplicity
    
    # Calculate required staff
    # Add some randomness for "called in sick" or "extra hands"
    variation = np.random.uniform(0.9, 1.1)
    
    n_waiters = max(2, int((items_sold / ROLES['Garzon']['capacity']) * variation))
    n_cooks = max(2, int((items_sold / ROLES['Cocinero']['capacity']) * variation))
    n_bartenders = max(1, int((items_sold / ROLES['Bartender']['capacity']) * variation))
    
    # Generate Shifts
    # Shift types: Opening (10-18), Closing (17-01), Full (11-23)
    shifts_to_fill = []
    
    # Distribute staff into shifts
    for role, count in [('Garzon', n_waiters), ('Cocinero', n_cooks), ('Bartender', n_bartenders)]:
        for i in range(count):
            shift_type = np.random.choice(['Apertura', 'Cierre', 'Intermedio'], p=[0.3, 0.5, 0.2])
            start_hour = 10 if shift_type == 'Apertura' else (17 if shift_type == 'Cierre' else 13)
            duration = 8
            
            staff_log.append({
                'date': date.date(),
                'role': role,
                'shift_type': shift_type,
                'hours_worked': duration,
                'hourly_rate': ROLES[role]['cost'],
                'total_pay': duration * ROLES[role]['cost'],
                'staff_id': f"{role[:3].upper()}-{np.random.randint(100, 999)}" # e.g., GAR-102
            })
            
    # Always 1 Admin
    staff_log.append({
        'date': date.date(),
        'role': 'Admin',
        'shift_type': 'Full',
        'hours_worked': 9,
        'hourly_rate': ROLES['Admin']['cost'],
        'total_pay': 9 * ROLES['Admin']['cost'],
        'staff_id': 'ADM-001'
    })

rrhh_df = pd.DataFrame(staff_log)
rrhh_df.to_csv('rrhh_turnos.csv', index=False)
print(f"[OK] Generated {len(rrhh_df)} staff shifts")

# ==========================================
# 2. REVIEWS (SENTIMENT)
# ==========================================
print("Generating Reviews data...")

REVIEWS_TEMPLATES = {
    'positive': [
        "Increíble vista al mar y la comida deliciosa.",
        "Las mejores pizzas de La Serena, masa muy crujiente.",
        "Excelente atención, el garzón fue muy amable.",
        "Un lugar perfecto para ver el atardecer con un pisco sour.",
        "Muy buen ambiente y música agradable.",
        "La tabla estación es gigante, perfecta para compartir.",
        "Rápido y rico, volveremos seguro.",
        "Me encantó la decoración con durmientes, muy original."
    ],
    'neutral': [
        "La comida bien, pero demoraron un poco.",
        "El lugar es lindo pero la música estaba muy fuerte.",
        "Precios un poco altos para la cantidad.",
        "Bien, pero nada extraordinario.",
        "La pizza estaba rica pero llegó tibia."
    ],
    'negative': [
        "Pésima experiencia, esperamos 1 hora por una pizza.",
        "El local estaba lleno y nadie nos atendía.",
        "La comida llegó fría y el garzón fue grosero.",
        "Muy caro para lo que ofrecen.",
        "No respetaron mi reserva, tuvimos que esperar de pie.",
        "El baño estaba sucio y descuidado."
    ]
}

reviews_log = []
prob_review = 0.05 # 5% of tables leave a review (approx)

for _, row in daily_stats.iterrows():
    # Base Traffic
    traffic = row['foot_traffic_estimate']
    n_reviews = np.random.binomial(traffic, prob_review)
    
    if n_reviews > 0:
        # Determine sentiment guided by "pressure"
        # High traffic relative to staff? -> Bad service
        # We don't have exact staff count here easily without re-aggregating, 
        # so let's use traffic volume as a proxy for stress.
        
        stress_factor = 0
        if traffic > 120: stress_factor = 0.3 # High stress
        
        for _ in range(n_reviews):
            # Roll for sentiment
            # Base: 70% Pos, 20% Neu, 10% Neg
            # Stressed: 50% Pos, 20% Neu, 30% Neg
            
            probs = [0.7, 0.2, 0.1]
            if stress_factor > 0:
                probs = [0.5, 0.2, 0.3]
            
            sentiment = np.random.choice(['positive', 'neutral', 'negative'], p=probs)
            
            # Select Text
            text = np.random.choice(REVIEWS_TEMPLATES[sentiment])
            
            # Generate Rating
            if sentiment == 'positive': rating = np.random.choice([4, 5])
            elif sentiment == 'neutral': rating = 3
            else: rating = np.random.choice([1, 2])
            
            reviews_log.append({
                'date': row['date'].date(),
                'platform': np.random.choice(['Google', 'TripAdvisor', 'Instagram'], p=[0.6, 0.3, 0.1]),
                'rating': rating,
                'text': text,
                'sentiment_label': sentiment
            })

reviews_df = pd.DataFrame(reviews_log)
reviews_df.to_csv('reviews_clientes.csv', index=False)
print(f"[OK] Generated {len(reviews_df)} reviews")


# ==========================================
# 3. RESERVATIONS (RESERVAS)
# ==========================================
print("Generating Reservations data...")
reservas_log = []

# Promo Days Logic -> NO RESERVATIONS
# Martes (Day 1), Jueves (Day 3), Fiestas Patrias (Sept 18, 19)
promo_days_indices = [1, 3] # Tue, Thu
promo_dates_str = [] # Fill with YYYY-09-18, etc.

# Helper for Fiestas Patrias check
def is_promo_date(d):
    # Check Day of Week
    if d.weekday() in promo_days_indices:
        return True
    # Check specific dates
    s = d.strftime('%m-%d')
    if s in ['09-18', '09-19']:
        return True
    return False

reservation_id_counter = 5000

for _, row in daily_stats.iterrows():
    curr_date = row['date']
    
    # 1. CHECK: Is this a blocked promo day?
    if is_promo_date(curr_date):
        continue # SKIP generation (Walk-in only)
        
    # Generate Reservations for Normal Days
    # Avg 30% of traffic is reserved
    traffic = row['foot_traffic_estimate']
    n_res = int(traffic * 0.30 * np.random.uniform(0.8, 1.2))
    
    for _ in range(n_res):
        pax = np.random.choice([2, 2, 4, 4, 6, 8], p=[0.3, 0.4, 0.15, 0.1, 0.03, 0.02])
        status = np.random.choice(['Show', 'No-Show', 'Cancelled'], p=[0.85, 0.10, 0.05])
        
        # Time distribution (Dinner focused)
        hour = np.random.choice([13, 14, 19, 20, 21, 22], p=[0.1, 0.1, 0.2, 0.3, 0.2, 0.1])
        time_str = f"{hour}:00"
        
        reservas_log.append({
            'reservation_id': f"RES-{reservation_id_counter}",
            'date': curr_date.date(),
            'time': time_str,
            'pax': pax,
            'customer_name': f"Cliente {reservation_id_counter}", # Anonymized
            'status': status,
            'channel': np.random.choice(['Web', 'Phone', 'WhatsApp'], p=[0.5, 0.2, 0.3])
        })
        reservation_id_counter += 1

reservas_df = pd.DataFrame(reservas_log)
reservas_df.to_csv('reservas.csv', index=False)
print(f"[OK] Generated {len(reservas_df)} reservations")

print("\n" + "="*50)
print("OPERATIONAL DATA GENERATION COMPLETE")
print("="*50)
