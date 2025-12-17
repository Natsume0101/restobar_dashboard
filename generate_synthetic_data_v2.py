"""
Restaurant Data Enrichment & Synthetic Data Generation - ENHANCED VERSION
Includes REAL promotions from @estacionlaserena Instagram
Generates ficha_tecnica.csv, ventas_sinteticas_3anos.csv, and mermas.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# Load promotions configuration
print("Loading promotions configuration...")
with open('promociones_reales.json', 'r', encoding='utf-8') as f:
    PROMOCIONES = json.load(f)

# Load historical sales data
print("Loading historical sales data...")
df = pd.read_csv('ventas_historicas_3anos.csv')
df['order_date'] = pd.to_datetime(df['order_date'])
df['revenue'] = df['item_price'] * df['quantity']

# Helper function to check if time is within promotion hours
def is_in_time_range(hour, start_time, end_time):
    """Check if hour is within promotion time range"""
    start_hour = int(start_time.split(':')[0])
    end_hour = int(end_time.split(':')[0])
    return start_hour <= hour <= end_hour

# Get unique items with categorization
items_summary = df.groupby(['item_name', 'item_type']).agg({
    'quantity': 'sum',
    'revenue': 'sum',
    'order_id': 'count',
    'item_price': 'first'
}).rename(columns={'order_id': 'num_orders'}).reset_index()

items_summary = items_summary.sort_values('revenue', ascending=False)

# Technical specifications database (realistic Chilean restaurant data - FROM MENU RESEARCH)
ficha_tecnica_data = {
    # BURGERS
    'Clásica': {
        'category': 'Burgers',
        'ingredients': json.dumps(['carne de vacuno (150g)', 'pan brioche', 'lechuga', 'tomate', 'cebolla', 'queso cheddar', 'mayonesa', 'ketchup']),
        'portion_g_ml': 350,
        'prep_time_min': 12,
        'cost_clp': 4200,
        'shelf_life_hours': 2,
        'calories': 680,
        'protein_g': 35,
        'carbs_g': 52,
        'allergens': json.dumps(['gluten', 'lácteos', 'huevo']),
        'notes': 'Hamburguesa clásica con carne premium 100% vacuno'
    },
    'Mechada Avocado': {
        'category': 'Burgers',
        'ingredients': json.dumps(['carne mechada (180g)', 'palta', 'pan brioche', 'lechuga', 'tomate', 'mayonesa casera']),
        'portion_g_ml': 380,
        'prep_time_min': 14,
        'cost_clp': 4800,
        'shelf_life_hours': 2,
        'calories': 745,
        'protein_g': 38,
        'carbs_g': 54,
        'allergens': json.dumps(['gluten', 'lácteos', 'huevo']),
        'notes': 'Carne mechada estilo chileno con palta Hass'
    },
    
    # PIZZAS
    'Margarita': {
        'category': 'Pizzas',
        'ingredients': json.dumps(['masa artesanal (300g)', 'salsa pomodoro', 'mozzarella', 'albahaca fresca', 'aceite de oliva']),
        'portion_g_ml': 450,
        'prep_time_min': 18,
        'cost_clp': 3200,
        'shelf_life_hours': 4,
        'calories': 580,
        'protein_g': 28,
        'carbs_g': 68,
        'allergens': json.dumps(['gluten', 'lácteos']),
        'notes': 'Pizza clásica italiana con ingredientes frescos'
    },
    'Pepperoni': {
        'category': 'Pizzas',
        'ingredients': json.dumps(['masa artesanal (300g)', 'salsa pomodoro', 'mozzarella', 'pepperoni (80g)', 'orégano']),
        'portion_g_ml': 480,
        'prep_time_min': 18,
        'cost_clp': 3800,
        'shelf_life_hours': 4,
        'calories': 720,
        'protein_g': 32,
        'carbs_g': 70,
        'allergens': json.dumps(['gluten', 'lácteos']),
        'notes': 'Pizza con pepperoni de cerdo ahumado'
    },
    'Cuatro Formaggi': {
        'category': 'Pizzas',
        'ingredients': json.dumps(['masa artesanal (300g)', 'salsa blanca', 'mozzarella', 'parmesano', 'gorgonzola', 'queso de cabra']),
        'portion_g_ml': 470,
        'prep_time_min': 20,
        'cost_clp': 4800,
        'shelf_life_hours': 4,
        'calories': 820,
        'protein_g': 38,
        'carbs_g': 66,
        'allergens': json.dumps(['gluten', 'lácteos']),
        'notes': 'Pizza gourmet con 4 quesos premium'
    },
    
    # PRINCIPALES
    'Valenciano': {
        'category': 'Principales',
        'ingredients': json.dumps(['arroz (200g)', 'mariscos mixtos (180g)', 'chorizo', 'pimentón', 'azafrán', 'caldo de pescado']),
        'portion_g_ml': 520,
        'prep_time_min': 25,
        'cost_clp': 6200,
        'shelf_life_hours': 3,
        'calories': 620,
        'protein_g': 42,
        'carbs_g': 78,
        'allergens': json.dumps(['mariscos', 'moluscos']),
        'notes': 'Paella valenciana con mariscos frescos'
    },
    'Salmón Tando': {
        'category': 'Principales',
        'ingredients': json.dumps(['filete de salmón (220g)', 'salsa tando', 'verduras salteadas', 'arroz basmati']),
        'portion_g_ml': 480,
        'prep_time_min': 20,
        'cost_clp': 7200,
        'shelf_life_hours': 2,
        'calories': 580,
        'protein_g': 48,
        'carbs_g': 42,
        'allergens': json.dumps(['pescado', 'sésamo', 'soya']),
        'notes': 'Salmón del Atlántico con marinado japonés'
    },
    'Filete Trifolatti': {
        'category': 'Principales',
        'ingredients': json.dumps(['filete lomo (250g)', 'salsa trifolatti', 'champiñones', 'papas rústicas', 'verduras']),
        'portion_g_ml': 550,
        'prep_time_min': 22,
        'cost_clp': 9800,
        'shelf_life_hours': 2,
        'calories': 720,
        'protein_g': 52,
        'carbs_g': 38,
        'allergens': json.dumps(['lácteos', 'hongos']),
        'notes': 'Filete premium con salsa de champiñones'
    },
    'Rocca Avocado': {
        'category': 'Principales',
        'ingredients': json.dumps(['pollo o carne (200g)', 'palta', 'rúcula', 'tomates cherry', 'parmesano', 'vinagreta']),
        'portion_g_ml': 420,
        'prep_time_min': 18,
        'cost_clp': 8500,
        'shelf_life_hours': 3,
        'calories': 620,
        'protein_g': 44,
        'carbs_g': 28,
        'allergens': json.dumps(['lácteos']),
        'notes': 'Plato mediterráneo con palta y rúcula'
    },
    
    # ENTRADAS
    'Camarón a la Vista': {
        'category': 'Entradas',
        'ingredients': json.dumps(['camarones (150g)', 'ajo', 'perejil', 'mantequilla', 'vino blanco', 'pan de ajo']),
        'portion_g_ml': 220,
        'prep_time_min': 15,
        'cost_clp': 5800,
        'shelf_life_hours': 2,
        'calories': 380,
        'protein_g': 28,
        'carbs_g': 18,
        'allergens': json.dumps(['mariscos', 'gluten', 'lácteos']),
        'notes': 'Camarones al ajillo estilo español'
    },
    'Arancini': {
        'category': 'Entradas',
        'ingredients': json.dumps(['arroz arborio (120g)', 'mozzarella', 'carne molida', 'salsa pomodoro', 'pan rallado']),
        'portion_g_ml': 180,
        'prep_time_min': 20,
        'cost_clp': 3800,
        'shelf_life_hours': 4,
        'calories': 420,
        'protein_g': 18,
        'carbs_g': 48,
        'allergens': json.dumps(['gluten', 'lácteos', 'huevo']),
        'notes': 'Croquetas sicilianas de arroz rellenas'
    },
    'Locos en su Emulsión': {
        'category': 'Entradas',
        'ingredients': json.dumps(['locos (200g)', 'mayonesa emulsionada', 'limón', 'cilantro', 'ajo']),
        'portion_g_ml': 250,
        'prep_time_min': 18,
        'cost_clp': 11500,
        'shelf_life_hours': 1,
        'calories': 320,
        'protein_g': 32,
        'carbs_g': 8,
        'allergens': json.dumps(['moluscos', 'huevo']),
        'notes': 'Manjar marino chileno con locos frescos'
    },
    
    # FRÍO Y FRESCOS
    'Tartar de Jaiba con Locos': {
        'category': 'Frío y Frescos',
        'ingredients': json.dumps(['jaiba (120g)', 'locos (80g)', 'palta', 'cebolla morada', 'cilantro', 'limón']),
        'portion_g_ml': 220,
        'prep_time_min': 12,
        'cost_clp': 8900,
        'shelf_life_hours': 1,
        'calories': 280,
        'protein_g': 24,
        'carbs_g': 12,
        'allergens': json.dumps(['mariscos', 'moluscos']),
        'notes': 'Tartar de mariscos premium chilenos'
    },
    'Duo del Mar': {
        'category': 'Frío y Frescos',
        'ingredients': json.dumps(['salmón fresco (100g)', 'atún (100g)', 'aguacate', 'pepino', 'salsa ponzu']),
        'portion_g_ml': 280,
        'prep_time_min': 10,
        'cost_clp': 7200,
        'shelf_life_hours': 1,
        'calories': 340,
        'protein_g': 38,
        'carbs_g': 14,
        'allergens': json.dumps(['pescado', 'soya', 'sésamo']),
        'notes': 'Ceviche duo de pescados frescos'
    },
    
    # POSTRES
    'Volcán de Chocolate': {
        'category': 'Postres',
        'ingredients': json.dumps(['chocolate belga (80g)', 'huevos', 'mantequilla', 'azúcar', 'harina', 'helado de vainilla']),
        'portion_g_ml': 180,
        'prep_time_min': 15,
        'cost_clp': 2100,
        'shelf_life_hours': 6,
        'calories': 520,
        'protein_g': 8,
        'carbs_g': 58,
        'allergens': json.dumps(['gluten', 'lácteos', 'huevo']),
        'notes': 'Coulant de chocolate con centro líquido'
    },
    'Pavlova (Papaya)': {
        'category': 'Postres',
        'ingredients': json.dumps(['merengue (100g)', 'crema chantilly', 'papaya', 'frutos rojos', 'coulis de fruta']),
        'portion_g_ml': 200,
        'prep_time_min': 12,
        'cost_clp': 2000,
        'shelf_life_hours': 4,
        'calories': 380,
        'protein_g': 4,
        'carbs_g': 62,
        'allergens': json.dumps(['lácteos', 'huevo']),
        'notes': 'Postre neozelandés con frutas tropicales'
    },
    
    # TABLAS
    'Tabla Estación': {
        'category': 'Tablas',
        'ingredients': json.dumps(['quesos variados (200g)', 'jamón serrano (150g)', 'salames (100g)', 'frutas', 'frutos secos', 'pan']),
        'portion_g_ml': 650,
        'prep_time_min': 8,
        'cost_clp': 14500,
        'shelf_life_hours': 3,
        'calories': 1240,
        'protein_g': 58,
        'carbs_g': 68,
        'allergens': json.dumps(['lácteos', 'gluten', 'frutos secos']),
        'notes': 'Tabla para compartir con selección premium'
    },
    
    # BEBIDAS
    'Jugo de Pulpa': {
        'category': 'Bebidas',
        'ingredients': json.dumps(['fruta natural (200g)', 'agua', 'azúcar opcional']),
        'portion_g_ml': 350,
        'prep_time_min': 5,
        'cost_clp': 800,
        'shelf_life_hours': 4,
        'calories': 120,
        'protein_g': 1,
        'carbs_g': 28,
        'allergens': json.dumps([]),
        'notes': 'Jugo natural de frutas de estación'
    },
    
    # VINOS
    'Copa de Vino CS': {
        'category': 'Vinos',
        'ingredients': json.dumps(['vino Cab. Sauvignon (150ml)', 'varietal chileno']),
        'portion_g_ml': 150,
        'prep_time_min': 2,
        'cost_clp': 1400,
        'shelf_life_hours': 48,
        'calories': 125,
        'protein_g': 0,
        'carbs_g': 4,
        'allergens': json.dumps(['sulfitos']),
        'notes': 'Copa de vino Cabernet Sauvignon chileno'
    }
}

# Create ficha_tecnica DataFrame WITH ACTUAL DATA
ficha_records = []
for item_name, specs in ficha_tecnica_data.items():
    ficha_records.append({
        'item_name': item_name,
        'category': specs['category'],
        'ingredients': specs['ingredients'],
        'portion_g_ml': specs['portion_g_ml'],
        'prep_time_min': specs['prep_time_min'],
        'cost_clp': specs['cost_clp'],
        'shelf_life_hours': specs['shelf_life_hours'],
        'calories': specs['calories'],
        'protein_g': specs['protein_g'],
        'carbs_g': specs['carbs_g'],
        'allergens': specs['allergens'],
        'notes': specs['notes']
    })

ficha_df = pd.DataFrame(ficha_records)
ficha_df.to_csv('ficha_tecnica.csv', index=False, encoding='utf-8')
print(f"[OK] Generated ficha_tecnica.csv with {len(ficha_df)} items")

print("\\n" + "="*70)
print("GENERATING ENHANCED DATA WITH REAL PROMOTIONS")
print("="*70)

# Date range: 3 years
start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Chilean holidays
holidays_2023_2025 = [
    '2023-01-01', '2023-04-07', '2023-05-01', '2023-09-18', '2023-09-19', '2023-12-25',
    '2024-01-01', '2024-03-29', '2024-05-01', '2024-09-18', '2024-09-19', '2024-12-25',
    '2025-01-01', '2025-04-18', '2025-05-01', '2025-09-18', '2025-09-19', '2025-12-25'
]
holidays_set = set(pd.to_datetime(holidays_2023_2025).date)

def get_temperature(date):
    """Get temperature based on Santiago climate"""
    month = date.month
    base_temps = {1: 24, 2: 25, 3: 20, 4: 16, 5: 12, 6: 9, 7: 8, 8: 10, 9: 14, 10: 18, 11: 21, 12: 23}
    return base_temps[month] + np.random.normal(0, 3)

def apply_promotion_logic(date, hour, item_name, item_type, base_price):
    """
    Apply promotion logic based on day, time, and item
    Returns: (final_price, quantity_multiplier, promo_type)
    """
    day_of_week = date.dayofweek
    date_str = date.strftime('%m-%d')
    
    # Check for special events first (highest priority)
    if 'fiestas_patrias' in PROMOCIONES['eventos_especiales']:
        fp = PROMOCIONES['eventos_especiales']['fiestas_patrias']
        if fp['activo'] and date_str in fp['fechas']:
            return base_price, fp['multiplicador_trafico'], 'fiestas_patrias'
    
    if 'navidad' in PROMOCIONES['eventos_especiales']:
        nav = PROMOCIONES['eventos_especiales']['navidad']
        if nav['activo'] and date_str in nav['fechas']:
            return base_price * 1.1, nav['multiplicador_ticket'], 'navidad'
    
    # Menú Ejecutivo (12:30-16:00 todos los días)
    menu_exec = PROMOCIONES['promociones_diarias']['menu_ejecutivo']
    if menu_exec['activo'] and is_in_time_range(hour, menu_exec['hora_inicio'], menu_exec['hora_fin']):
        if item_name in menu_exec['items_principales']:
            if np.random.random() < menu_exec['probabilidad_completo']:
                return menu_exec['precio_completo'], 1.0, 'menu_ejecutivo_completo'
            else:
                return menu_exec['precio_basico'], 1.0, 'menu_ejecutivo_basico'
    
    # Martes Pizza Libre
    pizza_libre = PROMOCIONES['promociones_semanales']['martes_pizza_libre']
    if pizza_libre['activo'] and day_of_week == pizza_libre['dia_semana']:
        if is_in_time_range(hour, pizza_libre['hora_inicio'], pizza_libre['hora_fin']):
            if item_name in pizza_libre['items_afectados']:
                return base_price, pizza_libre['multiplicador_cantidad'], 'pizza_libre'
    
    # Jueves Ladies Night (50% descuento 21:00-00:00)
    ladies_night = PROMOCIONES['promociones_semanales']['jueves_ladies_night']
    if ladies_night['activo'] and day_of_week == ladies_night['dia_semana']:
        if is_in_time_range(hour, ladies_night['hora_inicio'], ladies_night['hora_fin']):
            discount = ladies_night['porcentaje_descuento'] / 100
            return int(base_price * (1 - discount)), ladies_night['multiplicador_trafico'], 'ladies_night_50'
    
    # After Office 2x1 (Lun-Vie 18:00-21:00)
    after_office = PROMOCIONES['promociones_semanales']['after_office']
    if after_office['activo'] and day_of_week in after_office['dias_semana']:
        if is_in_time_range(hour, after_office['hora_inicio'], after_office['hora_fin']):
            if item_name in after_office['items_afectados']:
                discount = after_office['porcentaje_descuento'] / 100
                return int(base_price * (1 - discount)), after_office['multiplicador_cantidad'], 'after_office_2x1'
    
    # Bar Nikkita (Vie-Sáb 23:00+)
    bar_nikkita = PROMOCIONES['promociones_semanales']['bar_nikkita_weekend']
    if bar_nikkita['activo'] and day_of_week in bar_nikkita['dias_semana']:
        if is_in_time_range(hour, bar_nikkita['hora_inicio'], bar_nikkita['hora_fin']):
            if item_name in bar_nikkita['items_afectados']:
                return int(base_price * bar_nikkita['multiplicador_ticket']), 1.2, 'bar_nikkita'
    
    # No promotion
    return base_price, 1.0, 'normal'

# Generate synthetic sales WITH PROMOTIONS
synthetic_sales = []
np.random.seed(42)

print("Generating sales data with promotional patterns...")
for date in date_range:
    is_holiday = date.date() in holidays_set
    is_weekend = date.dayofweek in [4, 5]
    temp = get_temperature(date)
    day_of_week = date.dayofweek
    
    # Base foot traffic
    foot_traffic = 80
    if is_weekend:
        foot_traffic += 40
    if is_holiday:
        foot_traffic += 30
    if temp > 25:
        foot_traffic += 10
    
    # Apply promotional traffic multipliers
    date_str = date.strftime('%m-%d')
    
    # Jueves Ladies Night boost
    if day_of_week == 3:  # Thursday
        ladies_night = PROMOCIONES['promociones_semanales']['jueves_ladies_night']
        foot_traffic = int(foot_traffic * ladies_night['multiplicador_trafico'])
    
    # Fiestas Patrias boost
    fp = PROMOCIONES['eventos_especiales']['fiestas_patrias']
    if date_str in fp['fechas']:
        foot_traffic = int(foot_traffic * fp['multiplicador_trafico'])
    
    foot_traffic = int(foot_traffic + np.random.normal(0, 15))
    foot_traffic = max(30, foot_traffic)
    
    # Simulate different service periods
    # Lunch (12:00-16:00), Dinner (19:00-23:00), Late Night (23:00-02:00)
    periods = [
        {'start': 12, 'end': 16, 'weight': 0.3},  # Lunch
        {'start': 19, 'end': 23, 'weight': 0.5},  # Dinner
        {'start': 23, 'end': 24, 'weight': 0.2}   # Late night
    ]
    
    for period in periods:
        period_orders = int(np.random.poisson(foot_traffic * period['weight'] * 0.6))
        
        for _ in range(period_orders):
            # Random hour within period
            hour = np.random.randint(period['start'], period['end'])
            
            # Weighted item selection
            item_weights = items_summary.set_index('item_name')['quantity'].to_dict()
            items_list = list(item_weights.keys())
            weights_list = [item_weights[item] for item in items_list]
            
            item = np.random.choice(items_list, p=np.array(weights_list)/sum(weights_list))
            item_info = items_summary[items_summary['item_name'] == item].iloc[0]
            base_price = item_info['item_price']
            item_type = item_info['item_type']
            
            # Apply promotional logic
            final_price, qty_multiplier, promo_type = apply_promotion_logic(
                date, hour, item, item_type, base_price
            )
            
            # Quantity (affected by promotions)
            base_qty = np.random.choice([1, 2, 3, 4], p=[0.6, 0.25, 0.10, 0.05])
            qty = int(base_qty * qty_multiplier)
            qty = max(1, min(qty, 10))  # Cap at 10
            
            revenue = final_price * qty
            
            synthetic_sales.append({
                'date': date.date(),
                'item_name': item,
                'item_type': item_type,
                'qty_sold': qty,
                'unit_price': int(final_price),
                'revenue': int(revenue),
                'promo_type': promo_type,
                'weather_temp': round(temp, 1),
                'foot_traffic_estimate': foot_traffic,
                'is_weekend': is_weekend,
                'is_holiday': is_holiday,
                'day_of_week': day_of_week,
                'hour': hour
            })

sales_df = pd.DataFrame(synthetic_sales)

# Add predictive features
sales_df = sales_df.sort_values('date')
sales_df['rolling_avg_sales_7d'] = sales_df.groupby('item_name')['qty_sold'].transform(
    lambda x: x.rolling(window=7, min_periods=1).mean()
)
sales_df['demand_forecast_next_day'] = sales_df['rolling_avg_sales_7d'] * np.random.uniform(0.9, 1.1, len(sales_df))

# Drop hour column for final output (was just for promo logic)
sales_df_output = sales_df.drop(columns=['hour'])
sales_df_output.to_csv('ventas_sinteticas_3anos.csv', index=False, encoding='utf-8')
print(f"[OK] Generated ventas_sinteticas_3anos.csv with {len(sales_df_output):,} rows")

# Generate Mermas WITH promotion-aware logic
print("\\nGenerating mermas (waste) data with promotional patterns...")
mermas_records = []
np.random.seed(43)

for date in date_range:
    daily_sales = sales_df[sales_df['date'] == date.date()]
    day_of_week = date.dayofweek
    
    for _, sale in daily_sales.iterrows():
        # Base waste probability: 10%
        waste_prob = 0.10
        
        # Increase waste after high-volume promo days
        # e.g., Wednesday after Martes Pizza Libre
        if day_of_week == 2 and sale['item_type'] == 'Pizzas':  # Wednesday pizzas
            waste_prob = 0.25
        
        # Friday after Thursday Ladies Night
        if day_of_week == 4:  # Friday
            waste_prob = 0.15
        
        if np.random.random() < waste_prob:
            item = sale['item_name']
            
            # Waste quantity (typically 1-2 units, more after promos)
            if sale['promo_type'] in ['pizza_libre', 'ladies_night_50']:
                merma_qty = np.random.choice([1, 2, 3], p=[0.5, 0.35, 0.15])
            else:
                merma_qty = np.random.choice([1, 2], p=[0.75, 0.25])
            
            # Waste reasons
            reasons = ['overprep', 'expired', 'quality_issue', 'damage']
            reason_probs = [0.50, 0.25, 0.15, 0.10]
            reason = np.random.choice(reasons, p=reason_probs)
            
            # Get cost from ficha tecnica
            cost = 2000  # default
            if item in ficha_tecnica_data:
                cost = ficha_tecnica_data[item]['cost_clp']
            
            value_lost = merma_qty * cost
            preventable = reason in ['overprep', 'damage', 'quality_issue']
            
            mermas_records.append({
                'date': date.date(),
                'item_name': item,
                'merma_qty': merma_qty,
                'reason': reason,
                'value_lost_clp': value_lost,
                'preventable': 'yes' if preventable else 'no',
                'related_promo': sale['promo_type']
            })

mermas_df = pd.DataFrame(mermas_records)
mermas_df.to_csv('mermas.csv', index=False, encoding='utf-8')
print(f"[OK] Generated mermas.csv with {len(mermas_df):,} rows")

# VALIDATION SUMMARY
print("\\n" + "="*70)
print("VALIDATION & SUMMARY REPORT WITH PROMOTIONS")
print("="*70)

print(f"\\n[*] DATASET STATISTICS:")
print(f"   • Synthetic Sales: {len(sales_df_output):,} records ({len(date_range)} days)")
print(f"   • Mermas: {len(mermas_df):,} waste records")

print(f"\\n[*] PROMOTION DISTRIBUTION:")
promo_dist = sales_df['promo_type'].value_counts()
for promo, count in promo_dist.items():
    pct = (count / len(sales_df)) * 100
    print(f"   • {promo}: {count:,} ({pct:.1f}%)")

print(f"\\n[*] REVENUE COMPARISON:")
historical_revenue = df['revenue'].sum()
synthetic_revenue = sales_df['revenue'].sum()
variance = ((synthetic_revenue - historical_revenue) / historical_revenue) * 100
print(f"   • Historical Revenue: ${historical_revenue:,.0f} CLP")
print(f"   • Synthetic Revenue:  ${synthetic_revenue:,.0f} CLP")
print(f"   • Variance: {variance:+.1f}%")

print(f"\\n[*] DAY-OF-WEEK ANALYSIS:")
dow_sales = sales_df.groupby('day_of_week').agg({
    'revenue': 'sum',
    'qty_sold': 'sum'
}).reset_index()
dow_sales['day_name'] = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
for _, row in dow_sales.iterrows():
    print(f"   • {row['day_name']}: ${row['revenue']:,.0f} CLP ({row['qty_sold']:,} items)")

print(f"\\n[*] TUESDAY PIZZA BOOST:")
tuesday_pizzas = sales_df[(sales_df['day_of_week'] == 1) & (sales_df['item_type'] == 'Pizzas')]['qty_sold'].sum()
other_day_pizzas = sales_df[(sales_df['day_of_week'] != 1) & (sales_df['item_type'] == 'Pizzas')]['qty_sold'].sum() / 6
boost_pct = (tuesday_pizzas / other_day_pizzas - 1) * 100
print(f"   • Tuesday: {tuesday_pizzas:,} pizzas")
print(f"   • Other days avg: {other_day_pizzas:.0f} pizzas")
print(f"   • Boost: +{boost_pct:.1f}%")

print(f"\\n[*] MERMAS ANALYSIS:")
total_waste_value = mermas_df['value_lost_clp'].sum()
preventable_waste = mermas_df[mermas_df['preventable'] == 'yes']['value_lost_clp'].sum()
print(f"   • Total Waste Value: ${total_waste_value:,.0f} CLP")
print(f"   • Preventable Waste: ${preventable_waste:,.0f} CLP ({preventable_waste/total_waste_value*100:.1f}%)")

print("\\n" + "="*70)
print("[SUCCESS] ALL FILES GENERATED WITH REAL PROMOTIONS!")
print("="*70)
print("\\nReady for machine learning and predictive analytics!")
