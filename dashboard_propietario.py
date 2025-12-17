
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Dashboard Propietario - Estación La Serena",
    page_icon="🍽️",
    layout="wide"
)

# ==========================================
# DATA LOADING (CACHED)
# ==========================================
@st.cache_data
def load_data():
    # Load ML Dataset
    df = pd.read_csv('dataset_ml_diario.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Load Raw Sales for Menu Analysis
    sales = pd.read_csv('ventas_sinteticas_3anos.csv')
    sales['date'] = pd.to_datetime(sales['date'])
    
    # Load Ficha Tecnica for Costs
    recipes = pd.read_csv('ficha_tecnica.csv')
    
    # Load Reviews
    reviews = pd.read_csv('reviews_clientes.csv')
    reviews['date'] = pd.to_datetime(reviews['date'])
    
    # Load Waste Data
    mermas = pd.read_csv('mermas.csv')
    mermas['date'] = pd.to_datetime(mermas['date'])
    
    return df, sales, recipes, reviews, mermas

@st.cache_resource
def train_model(df):
    # Train simple model on the fly for the dashboard
    # Split
    train_df = df[df['date'] < '2025-01-01']
    feature_cols = [
        'weather_temp', 'is_weekend', 'is_holiday', 'foot_traffic_estimate',
        'day_of_week', 'promo_pizza_tuesday', 'promo_ladies_thursday',
        'revenue_t-1', 'revenue_t-7'
    ]
    # Simple imputation for demo
    train_df = train_df.dropna(subset=feature_cols)
    
    X = train_df[feature_cols]
    y = train_df['target_revenue']
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    return model, feature_cols

# Load EVERYTHING
try:
    df, sales, recipes, reviews, mermas = load_data()
    model, features = train_model(df)
    DATA_LOADED = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    DATA_LOADED = False

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("👨‍🍳 Estación La Serena")
st.sidebar.info("**Modo Propietario**")
st.sidebar.markdown("---")
view_mode = st.sidebar.radio("Ir a:", ["📊 Bola de Cristal (Predicción)", "🍔 Ingeniería de Menú", "⭐ Salud Operacional", "⏳ Historia & Tendencias"])

if DATA_LOADED:
    
    # ==========================================
    # TAB 1: BOLA DE CRISTAL
    # ==========================================
    if view_mode == "📊 Bola de Cristal (Predicción)":
        st.title("🔮 Predicción de Demanda & Turnos")
        st.markdown("Planifica tu semana con Inteligencia Artificial.")
        
        # Forecast for next 7 days (Simulation)
        # We take the LAST known days from dataset to simulate 'next week' context
        last_date = df['date'].max()
        start_pred = last_date + timedelta(days=1)
        future_dates = [start_pred + timedelta(days=i) for i in range(7)]
        
        future_data = []
        for d in future_dates:
            # Simulate features for future
            dow = d.weekday()
            is_weekend = 1 if dow >= 5 else 0
            # Assuming recent averages for lags (simplified for dashboard demo)
            recent_rev = df.iloc[-1]['target_revenue']
            
            row = {
                'date': d,
                'weather_temp': 22, # Forecasted temp
                'is_weekend': is_weekend,
                'is_holiday': 0,
                'foot_traffic_estimate': 80 + (40 if is_weekend else 0) + (100 if dow==3 else 0), # Ladies night Logic
                'day_of_week': dow,
                'promo_pizza_tuesday': 1 if dow == 1 else 0,
                'promo_ladies_thursday': 1 if dow == 3 else 0,
                'revenue_t-1': recent_rev,
                'revenue_t-7': recent_rev # Naive lag
            }
            future_data.append(row)
            
        future_df = pd.DataFrame(future_data)
        
        # Predict
        preds = model.predict(future_df[features])
        future_df['pred_revenue'] = preds
        future_df['rec_staff'] = (future_df['pred_revenue'] / 40000).astype(int) # 1 staff per 40k revenue approx
        
        # KPIs
        col1, col2, col3 = st.columns(3)
        total_proj = future_df['pred_revenue'].sum()
        busiest_day = future_df.loc[future_df['pred_revenue'].idxmax()]['date'].strftime('%A')
        
        col1.metric("Venta Proyectada (7d)", f"${total_proj:,.0f}")
        col2.metric("Día Más Fuerte", busiest_day)
        col3.metric("Garzones Extra Jueves", "+2 (Ladies Night)")
        
        # Chart
        fig = px.line(future_df, x='date', y='pred_revenue', title="Proyección de Venta Diaria", markers=True)
        fig.update_layout(yaxis_title="Venta CLP ($)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Staffing Table
        st.subheader("📋 Recomendación de Turnos")
        staff_table = future_df[['date', 'pred_revenue', 'rec_staff']].copy()
        staff_table['date'] = staff_table['date'].dt.strftime('%Y-%m-%d (%A)')
        staff_table.columns = ['Fecha', 'Venta Estimada', 'Garzones Sugeridos']
        st.dataframe(staff_table, hide_index=True)

    # ==========================================
    # TAB 2: INGENIERIA DE MENU
    # ==========================================
    elif view_mode == "🍔 Ingeniería de Menú":
        st.title("🍔 Matriz de Rentabilidad (BCG)")
        st.markdown("¿Qué platos son tus **Estrellas** y cuáles son tus **Perros**?")
        
        with st.expander("ℹ️ ¿Qué significan estas categorías?", expanded=False):
            st.markdown("""
            *   **Star ⭐ (Estrella):** Alta Popularidad y Alta Rentabilidad. ¡Cuídalos! Son el motor de tu negocio.
            *   **Plowhorse 🐎 (Caballito de Batalla):** Alta Popularidad pero Baja Rentabilidad. Traen gente, pero ganas poco. Considera subir el precio o bajar costos.
            *   **Puzzle ❓ (Incógnita):** Baja Popularidad pero Alta Rentabilidad. Son platos rentables que la gente no pide. ¿Falta marketing? ¿Mejorar la foto?
            *   **Dog 🐕 (Perro):** Baja Popularidad y Baja Rentabilidad. Evalúa eliminarlos del menú.
            """)
        
        # Calculate Item Metrics
        item_stats = sales.groupby('item_name').agg({
            'qty_sold': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Merge with Cost
        menu_df = pd.merge(item_stats, recipes[['item_name', 'cost_clp', 'category']], on='item_name')
        menu_df['avg_price'] = menu_df['revenue'] / menu_df['qty_sold']
        menu_df['margin_clp'] = menu_df['avg_price'] - menu_df['cost_clp']
        menu_df['total_profit'] = menu_df['margin_clp'] * menu_df['qty_sold']
        
        # Classification
        # Star: High Vol, High Margin
        # Plowhorse: High Vol, Low Margin
        # Puzzle: Low Vol, High Margin
        # Dog: Low Vol, Low Margin
        
        med_vol = menu_df['qty_sold'].median()
        med_margin = menu_df['margin_clp'].median()
        
        def classify(row):
            if row['qty_sold'] >= med_vol and row['margin_clp'] >= med_margin: return 'Star ⭐'
            if row['qty_sold'] >= med_vol and row['margin_clp'] < med_margin: return 'Plowhorse 🐎'
            if row['qty_sold'] < med_vol and row['margin_clp'] >= med_margin: return 'Puzzle ❓'
            return 'Dog 🐕'
            
        menu_df['class'] = menu_df.apply(classify, axis=1)
        
        # Scatter Plot
        fig = px.scatter(
            menu_df, 
            x='qty_sold', 
            y='margin_clp', 
            size='revenue', 
            color='class',
            hover_name='item_name',
            text='item_name',
            title="Matriz de Popularidad vs Rentabilidad",
            color_discrete_map={'Star ⭐': 'green', 'Dog 🐕': 'red', 'Plowhorse 🐎': 'orange', 'Puzzle ❓': 'blue'}
        )
        fig.add_hline(y=med_margin, line_dash="dash", annotation_text="Margen Medio")
        fig.add_vline(x=med_vol, line_dash="dash", annotation_text="Volumen Medio")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(menu_df[['item_name', 'class', 'qty_sold', 'margin_clp', 'total_profit']].sort_values('total_profit', ascending=False))

    # ==========================================
    # TAB 3: SALUD OPERACIONAL
    # ==========================================
    elif view_mode == "⭐ Salud Operacional":
        st.title("⭐ Calidad vs Presión Operativa")
        
        col1, col2 = st.columns(2)
        
        # Avg Rating trend
        monthly_rating = reviews.set_index('date').resample('M')['rating'].mean().reset_index()
        fig_rating = px.line(monthly_rating, x='date', y='rating', title="Evolución de Calificación Promedio")
        col1.plotly_chart(fig_rating)
        
        # Sentiment Dist
        fig_sent = px.pie(reviews, names='sentiment_label', title="Sentimiento de Clientes", color='sentiment_label',
                         color_discrete_map={'positive':'green', 'neutral':'grey', 'negative':'red'})
        col2.plotly_chart(fig_sent)
        
        st.subheader("⚠️ Alertas de Calidad")
        # Filter negative reviews
        bad_reviews = reviews[reviews['sentiment_label'] == 'negative'].sort_values('date', ascending=False).head(5)
        for _, row in bad_reviews.iterrows():
            st.error(f"**{row['date'].date()} ({row['platform']})**: {row['text']}")

    # ==========================================
    # TAB 4: HISTORIA & TENDENCIAS
    # ==========================================
    elif view_mode == "⏳ Historia & Tendencias":
        st.title("⏳ Historia & Tendencias")
        st.markdown("Explora el comportamiento histórico de tu negocio: Ventas, Mermas, Clima y Clientes.")
        
        # Tabs for specific deep dives
        tab1, tab2, tab3, tab4 = st.tabs(["💰 Ventas Históricas", "🗑️ Análisis de Mermas", "🌤️ Impacto del Clima", "🗣️ Evolución Reviews"])
        
        # --- TAB 1: VENTAS ---
        with tab1:
            st.subheader("Evolución de Ventas")
            
            # Monthly Aggregation
            sales_monthly = df.set_index('date').resample('M')['target_revenue'].sum().reset_index()
            
            fig_sales = px.line(sales_monthly, x='date', y='target_revenue', title="Venta Mensual (3 Años)", markers=True)
            fig_sales.update_yaxes(title="Venta Total ($)")
            st.plotly_chart(fig_sales, use_container_width=True)
            
            # Day of Week Analysis
            st.subheader("Días más Fuertes")
            dow_map = {0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'}
            df['day_name'] = df['day_of_week'].map(dow_map)
            sales_dow = df.groupby('day_name')['target_revenue'].mean().reindex(['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']).reset_index()
            
            fig_dow = px.bar(sales_dow, x='day_name', y='target_revenue', title="Venta Promedio por Día de Semana", color='target_revenue')
            st.plotly_chart(fig_dow, use_container_width=True)

        # --- TAB 2: MERMAS ---
        with tab2:
            st.subheader("Control de Mermas")
            
            col1, col2 = st.columns(2)
            
            # Total Waste Cost over time (Monthly)
            waste_monthly = mermas.set_index('date').resample('M')['value_lost_clp'].sum().reset_index()
            fig_waste_trend = px.area(waste_monthly, x='date', y='value_lost_clp', title="Costo de Mermas Mensual", color_discrete_sequence=['red'])
            col1.plotly_chart(fig_waste_trend, use_container_width=True)
            
            # Waste by Reason
            waste_reason = mermas.groupby('reason')['value_lost_clp'].sum().reset_index()
            fig_reason = px.pie(waste_reason, values='value_lost_clp', names='reason', title="Causas de Merma (Dinero perdido)")
            col2.plotly_chart(fig_reason, use_container_width=True)
            
            st.dataframe(mermas.sort_values('date', ascending=False).head(10), use_container_width=True)

        # --- TAB 3: CLIMA ---
        with tab3:
            st.subheader("🌤️ ¿Influye el Clima en la Venta?")
            
            # Scattering Revenue vs Temp
            fig_weather = px.scatter(
                df, 
                x='weather_temp', 
                y='target_revenue', 
                color='is_weekend', 
                title="Venta vs Temperatura",
                labels={'weather_temp': 'Temperatura (°C)', 'target_revenue': 'Venta ($)', 'is_weekend': 'Es Finde'},
                trendline="ols" # Requires statsmodels
            )
            st.plotly_chart(fig_weather, use_container_width=True)
            
            st.info("💡 **Insight:** Observa si la nube de puntos sube a medida que aumenta la temperatura. La línea de tendencia indica la correlación.")

        # --- TAB 4: REVIEWS ---
        with tab4:
            st.subheader("❤️ Evolución de la Felicidad del Cliente")
            
            # Monthly Sentiment Count
            reviews['month'] = reviews['date'].dt.to_period('M').astype(str)
            sentiment_trend = reviews.groupby(['month', 'sentiment_label']).size().reset_index(name='count')
            
            fig_reviews = px.bar(
                sentiment_trend, 
                x='month', 
                y='count', 
                color='sentiment_label', 
                title="Cantidad de Reviews por Sentimiento (Mensual)",
                color_discrete_map={'positive':'green', 'neutral':'grey', 'negative':'red'},
                barmode='stack'
            )
            st.plotly_chart(fig_reviews, use_container_width=True) # type: ignore

else:
    st.warning("Cargando datos... si esto persiste, verifica que los archivos CSV existan.")
