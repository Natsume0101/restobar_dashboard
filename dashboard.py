import streamlit as st
import pandas as pd
import plotly.express as px

# Setting Page Configuration
st.set_page_config(
    page_title="La Estación Restobar - Dashboard",
    page_icon="🍽️",
    layout="wide"
)

# 1. Data Loading Function (Cached)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('ventas_historicas_3anos.csv')
        df['order_date'] = pd.to_datetime(df['order_date'])
        # Calculate Total Price (assuming item_price is per unit)
        df['total_line_price'] = df['item_price'] * df['quantity']
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 2. Sidebar Filters
    st.sidebar.header("Filtros")
    
    # Date Filter
    min_date = df['order_date'].min().date()
    max_date = df['order_date'].max().date()
    
    start_date = st.sidebar.date_input("Fecha Inicio", min_date)
    end_date = st.sidebar.date_input("Fecha Fin", max_date)
    
    # Category Filter
    categories = sorted(df['item_type'].unique())
    selected_categories = st.sidebar.multiselect("Categoría", categories, default=categories)
    
    # Filter Data logic
    mask = (
        (df['order_date'].dt.date >= start_date) & 
        (df['order_date'].dt.date <= end_date) &
        (df['item_type'].isin(selected_categories))
    )
    filtered_df = df[mask]
    
    # 3. Main Dashboard Title
    st.title("📊 Dashboard de Ventas - La Estación Restobar")
    st.markdown(f"**Periodo:** {start_date} a {end_date}")
    
    # 4. KPI Section
    kpi1, kpi2, kpi3 = st.columns(3)
    
    total_revenue = filtered_df['total_line_price'].sum()
    total_orders = filtered_df['order_id'].nunique()
    total_items = filtered_df['quantity'].sum()
    
    kpi1.metric("Ventas Totales (CLP)", f"${total_revenue:,.0f}".replace(",", "."))
    kpi2.metric("Total Órdenes", f"{total_orders:,}".replace(",", "."))
    kpi3.metric("Ítems Vendidos", f"{total_items:,}".replace(",", "."))
    
    st.markdown("---")
    
    # 5. Charts
    col1, col2 = st.columns(2)
    
    # Chart 1: Sales Trend
    with col1:
        st.subheader("Tendencia de Ventas (Mensual)")
        # Resample logic depending on filtered range could be dynamic, but fixed to Monthly for now
        monthly_sales = filtered_df.set_index('order_date').resample('M')['total_line_price'].sum().reset_index()
        fig_trend = px.line(monthly_sales, x='order_date', y='total_line_price', 
                            title='Ventas Mensuales', markers=True,
                            labels={'total_line_price': 'Ventas ($)', 'order_date': 'Mes'})
        fig_trend.update_layout(yaxis_tickformat="$,.0f")
        st.plotly_chart(fig_trend, use_container_width=True)
        
    # Chart 2: Revenue by Category (Pie/Donut)
    with col2:
        st.subheader("Ventas por Categoría")
        cat_sales = filtered_df.groupby('item_type')['total_line_price'].sum().reset_index()
        fig_cat = px.pie(cat_sales, values='total_line_price', names='item_type', 
                         title='Distribución de Ingresos', hole=0.4)
        st.plotly_chart(fig_cat, use_container_width=True)
        
    # Chart 3: Top Selling Items (Bar)
    st.subheader("Top 10 Productos Más Vendidos")
    top_items = filtered_df.groupby('item_name')['quantity'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bar = px.bar(top_items, x='quantity', y='item_name', orientation='h', 
                     title="Top 10 Productos (Cantidad)", text='quantity',
                     labels={'quantity': 'Cantidad', 'item_name': 'Producto'})
    fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # 6. Raw Data View
    with st.expander("Ver Datos Crudos"):
        st.dataframe(filtered_df.sort_values(by='order_date', ascending=False))
        
else:
    st.warning("No se pudieron cargar los datos. Verifique si el archivo CSV existe.")
