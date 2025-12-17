
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
import google.generativeai as genai
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
view_mode = st.sidebar.radio("Ir a:", ["📊 Bola de Cristal (Predicción)", "🍔 Ingeniería de Menú", "⭐ Salud Operacional", "⏳ Historia & Tendencias", "🤖 Asistente Virtual"])

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
        
        # Scatter Plot Enhanced
        fig = px.scatter(
            menu_df, 
            x='qty_sold', 
            y='margin_clp', 
            size='revenue', 
            color='class',
            hover_name='item_name',
            text='item_name',
            title="Matriz de Ingeniería de Menú (Popularidad vs Rentabilidad)",
            labels={'qty_sold': 'Popularidad (Unidades Vendidas)', 'margin_clp': 'Rentabilidad (Margen Unitario $)'},
            color_discrete_map={'Star ⭐': '#2ecc71', 'Dog 🐕': '#e74c3c', 'Plowhorse 🐎': '#f1c40f', 'Puzzle ❓': '#3498db'}
        )

        # Calculate max values for shapes
        max_x = menu_df['qty_sold'].max() * 1.1
        max_y = menu_df['margin_clp'].max() * 1.1
        min_x = 0
        min_y = 0 # Assuming positive margins generally, or set to min

        # Add Background Zones (Quadrants)
        fig.update_layout(
            shapes=[
                # Star (Top-Right) - Green
                dict(type="rect", x0=med_vol, y0=med_margin, x1=max_x, y1=max_y, fillcolor="rgba(46, 204, 113, 0.1)", line=dict(width=0), layer="below"),
                # Plowhorse (Bottom-Right) - Yellow
                dict(type="rect", x0=med_vol, y0=min_y, x1=max_x, y1=med_margin, fillcolor="rgba(241, 196, 15, 0.1)", line=dict(width=0), layer="below"),
                # Puzzle (Top-Left) - Blue
                dict(type="rect", x0=min_x, y0=med_margin, x1=med_vol, y1=max_y, fillcolor="rgba(52, 152, 219, 0.1)", line=dict(width=0), layer="below"),
                # Dog (Bottom-Left) - Red
                dict(type="rect", x0=min_x, y0=min_y, x1=med_vol, y1=med_margin, fillcolor="rgba(231, 76, 60, 0.1)", line=dict(width=0), layer="below"),
            ],
            annotations=[
                dict(x=(med_vol+max_x)/2, y=(med_margin+max_y)/2, text="ESTRELLA ⭐", showarrow=False, font=dict(size=20, color="green", weight="bold")),
                dict(x=(med_vol+max_x)/2, y=med_margin/2, text="CABALLITO 🐎", showarrow=False, font=dict(size=20, color="orange", weight="bold")),
                dict(x=med_vol/2, y=(med_margin+max_y)/2, text="PUZZLE ❓", showarrow=False, font=dict(size=20, color="blue", weight="bold")),
                dict(x=med_vol/2, y=med_margin/2, text="PERRO 🐕", showarrow=False, font=dict(size=20, color="red", weight="bold")),
            ]
        )
        
        fig.add_hline(y=med_margin, line_dash="dash", line_color="gray", annotation_text="Margen Medio")
        fig.add_vline(x=med_vol, line_dash="dash", line_color="gray", annotation_text="Volumen Medio")
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

    # ==========================================
    # TAB 5: ASISTENTE VIRTUAL (GEMINI)
    # ==========================================
    elif view_mode == "🤖 Asistente Virtual":
        st.title("🤖 Asistente Virtual (Powered by Gemini)")
        st.markdown("Pregúntale a tu dashboard. Ejemplo: *'¿Cuál fue el plato más vendido?'* o *'¿Cómo reducir mermas?'*")
        
        # 1. API Key Input
        api_key = st.sidebar.text_input("Ingresa tu Gemini API Key:", type="password", help="Consíguela en aistudio.google.com")
        
        # 2. Context Builder Function
        def get_dashboard_context(df, sales, mermas, reviews):
            # --- 1. GENERAL METRICS (3 Years) ---
            total_rev = df['target_revenue'].sum()
            avg_daily_rev = df['target_revenue'].mean()
            total_days = df['date'].nunique()
            
            # --- 2. MONTHLY ANALYSIS (Best/Worst) ---
            # Group Sales by Month
            df['month_str'] = df['date'].dt.to_period('M').astype(str)
            monthly_sales = df.groupby('month_str')['target_revenue'].sum().reset_index()
            
            best_month_row = monthly_sales.loc[monthly_sales['target_revenue'].idxmax()]
            worst_month_row = monthly_sales.loc[monthly_sales['target_revenue'].idxmin()]
            
            # Group Waste by Month
            mermas['month_str'] = mermas['date'].dt.to_period('M').astype(str)
            monthly_waste = mermas.groupby('month_str')['value_lost_clp'].sum().reset_index()
            
            # Merge to find waste for best/worst sales months
            def get_waste_for_month(m_str):
                row = monthly_waste[monthly_waste['month_str'] == m_str]
                return row['value_lost_clp'].values[0] if not row.empty else 0
                
            waste_at_best = get_waste_for_month(best_month_row['month_str'])
            waste_at_worst = get_waste_for_month(worst_month_row['month_str'])

            # --- 3. MENU ENGINEERING (Stars/Dogs) ---
            item_stats = sales.groupby('item_name').agg({'qty_sold': 'sum', 'revenue': 'sum'}).reset_index()
            # Approximate cost/margin calculation just for context (simplified)
            # merging with recipes if available in scope, but assuming basic rank here 
            # or re-using the logic from Tab 2 if possible. 
            # For robustness, we'll just use Top Selling (Stars) and Bottom Selling (Dogs candidates) by revenue
            top_5_items = item_stats.sort_values('revenue', ascending=False).head(5)
            bottom_5_items = item_stats.sort_values('revenue', ascending=True).head(5)
            
            stars_str = ", ".join([f"{r['item_name']} (${r['revenue']:,.0f})" for _, r in top_5_items.iterrows()])
            dogs_str = ", ".join([f"{r['item_name']} (${r['revenue']:,.0f})" for _, r in bottom_5_items.iterrows()])

            # --- 4. CALENDAR PATTERNS ---
            dow_map = {0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'}
            df['day_name'] = df['day_of_week'].map(dow_map)
            dow_sales = df.groupby('day_name')['target_revenue'].mean().sort_values(ascending=False)
            best_day = dow_sales.index[0]
            worst_day = dow_sales.index[-1]

            # --- 5. RECENT TRENDS (Last 6 Months) ---
            last_6_months = monthly_sales.tail(6)
            trend_str = ", ".join([f"{r['month_str']}: ${r['target_revenue']:,.0f}" for _, r in last_6_months.iterrows()])
            
            context = f"""
            Eres un experto analista de datos de restaurantes (Dueño de 'Estación La Serena'). 
            Tienes acceso a la historia completa de 3 AÑOS de datos. Usa esta información para responder:

            DATOS GENERALES:
            - Venta Total Histórica: ${total_rev:,.0f} (en {total_days} días operados)
            - Venta Promedio Diaria: ${avg_daily_rev:,.0f}

            HITS & FRACASOS (VENTAS MENSUALES):
            - 🏆 MEJOR MES DE LA HISTORIA: {best_month_row['month_str']} con ventas de ${best_month_row['target_revenue']:,.0f}. (Merma ese mes: ${waste_at_best:,.0f})
            - ⚠️ PEOR MES DE LA HISTORIA: {worst_month_row['month_str']} con ventas de ${worst_month_row['target_revenue']:,.0f}. (Merma ese mes: ${waste_at_worst:,.0f})

            INGENIERÍA DE MENÚ:
            - ⭐ Platos Super Estrellas (Top Ingresos): {stars_str}
            - 🐕 Platos Perro (Menos Ingresos, candidatos a eliminar): {dogs_str}

            PATRONES SEMANALES:
            - Día Más Fuerte: {best_day} (Promedio: ${dow_sales[0]:,.0f})
            - Día Más Débil: {worst_day} (Promedio: ${dow_sales[-1]:,.0f})

            TENDENCIA RECIENTE (Últimos 6 Meses):
            - Evolución: {trend_str}
            
            QUEJAS RECIENTES:
            - {reviews[reviews['sentiment_label'] == 'negative'].sort_values('date', ascending=False).head(3)['text'].tolist()}

            Instrucciones:
            1. Si te preguntan por ventas/mermas, cruza los datos de "Mejor Mes" vs su merma.
            2. Si te preguntan qué platos sacar, sugiere los "Perro".
            3. Sé directo y usa emojis.
            """
            return context

        # 3. Chat Logic
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Escribe tu pregunta aquí..."):
            # Visualize User Message
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Generate Response
            if not api_key:
                response_text = "⚠️ Por favor ingresa tu API Key de Google Gemini en la barra lateral para que pueda responderte."
            else:
                try:
                    genai.configure(api_key=api_key)
                    
                    # Attempt to find a supported model dynamically
                    active_model_name = 'gemini-pro' # Default fallback
                    try:
                        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        # Prefer 1.5 Flash, then Pro, then whatever is available
                        preferences = ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.0-pro']
                        
                        found_model = None
                        for pref in preferences:
                            if pref in available_models:
                                found_model = pref
                                break
                        
                        if found_model:
                            active_model_name = found_model
                        elif available_models:
                            active_model_name = available_models[0] # Pick the first available one
                            
                    except Exception as e:
                        # Fallback if listing fails
                        pass

                    model = genai.GenerativeModel(active_model_name)
                    
                    with st.expander("Detalles Técnicos", expanded=False):
                        st.caption(f"🤖 Modelo conectado: {active_model_name}")
                    
                    context = get_dashboard_context(df, sales, mermas, reviews)
                    full_prompt = f"{context}\n\nPregunta del Usuario: {prompt}"
                    
                    with st.spinner("Pensando..."):
                        response = model.generate_content(full_prompt)
                        response_text = response.text
                except Exception as e:
                    response_text = f"❌ Error al conectar con Gemini: {str(e)}"
            
            # Visualize AI Message
            with st.chat_message("assistant"):
                st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

else:
    st.warning("Cargando datos... si esto persiste, verifica que los archivos CSV existan.")
