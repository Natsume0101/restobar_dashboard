import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create output directory
os.makedirs('output', exist_ok=True)

# Load Data
try:
    df = pd.read_csv('ventas_historicas_3anos.csv')
    df['order_date'] = pd.to_datetime(df['order_date'])
    # Calculate Total Price for each row (assuming item_price is per unit)
    df['total_line_price'] = df['item_price'] * df['quantity']
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

print("--- ANALYSIS START ---")

# --- Objective 1: Menu Items Analysis ---
print("\n### Objective 1: Menu Items Analysis")
unique_items = df['item_name'].unique()
num_unique_items = len(unique_items)
print(f"1. Total Unique Menu Items: {num_unique_items}")

# Most and Least Expensive Items (unit price)
# Drop duplicates to get unique menu items list with their prices
menu_df = df[['item_name', 'item_type', 'item_price']].drop_duplicates()
max_price_item = menu_df.loc[menu_df['item_price'].idxmax()]
min_price_item = menu_df.loc[menu_df['item_price'].idxmin()]
print(f"2. Most Expensive: {max_price_item['item_name']} (${max_price_item['item_price']})")
print(f"   Least Expensive: {min_price_item['item_name']} (${min_price_item['item_price']})")

# Items per category
items_per_category = menu_df['item_type'].value_counts()
print("\n3. Items per Category:")
print(items_per_category.to_string())

# Avg price per category
avg_price_category = menu_df.groupby('item_type')['item_price'].mean().sort_values(ascending=False)
print("\n4. Average Price per Category:")
print(avg_price_category.to_string())

# Italian-style (Pizzas)
pizzas = menu_df[menu_df['item_type'] == 'Pizzas']
pizza_min = pizzas['item_price'].min()
pizza_max = pizzas['item_price'].max()
print(f"\n5. Italian-style (Pizzas) Price Range: ${pizza_min} - ${pizza_max}")


# --- Objective 2: Order Details Analysis ---
print("\n### Objective 2: Order Details Analysis")
date_min = df['order_date'].min().date()
date_max = df['order_date'].max().date()
print(f"1. Date Range: {date_min} to {date_max}")

total_orders = df['order_id'].nunique()
total_items_sold = df['quantity'].sum()
print(f"2. Total Unique Orders: {total_orders}")
print(f"   Total Items Sold: {total_items_sold}")

# Largest order by quantity
order_sizes = df.groupby('order_id')['quantity'].sum()
largest_order_id = order_sizes.idxmax()
largest_order_qty = order_sizes.max()
print(f"3. Largest Order (Quantity): {largest_order_id} with {largest_order_qty} items")

# Orders with > 12 items
orders_gt_12 = order_sizes[order_sizes > 12]
print(f"4. Count of Orders with >12 items: {len(orders_gt_12)}")
if len(orders_gt_12) > 0:
    print(f"   Sample IDs: {orders_gt_12.head(3).index.tolist()}...")


# --- Objective 3: Customer Behavior Analysis ---
print("\n### Objective 3: Customer Behavior Analysis")

# Top 5 Most and Least ordered items (by quantity)
item_popularity = df.groupby('item_name')['quantity'].sum().sort_values(ascending=False)
print("\n1. Top 5 MOST Ordered Items:")
print(item_popularity.head(5).to_string())
print("\n   Top 5 LEAST Ordered Items:")
print(item_popularity.tail(5).to_string())

# Revenue breakdown by category
revenue_by_cat = df.groupby('item_type')['total_line_price'].sum().sort_values(ascending=False)
print("\n2. Revenue Breakdown by Category:")
print(revenue_by_cat.to_string())

# Top 5 highest-spending orders
order_revenue = df.groupby('order_id')['total_line_price'].sum().sort_values(ascending=False)
top_5_orders = order_revenue.head(5)
print("\n3. Top 5 Highest-Spending Orders:")
print(top_5_orders.to_string())

# Details of #1 Highest Spending Order
top_order_id = top_5_orders.index[0]
top_order_details = df[df['order_id'] == top_order_id]
print(f"\n   Details of #1 Highest Spender ({top_order_id}):")
print(top_order_details[['item_name', 'item_type', 'quantity', 'item_price', 'total_line_price']].to_string())


# --- Charts ---
# 1. Monthly Sales Trend
monthly_sales = df.set_index('order_date').resample('M')['total_line_price'].sum()
plt.figure(figsize=(10, 6))
monthly_sales.plot(kind='line', marker='o', color='green')
plt.title('Monthly Sales Trend (2023-2025)')
plt.ylabel('Revenue ($)')
plt.grid(True)
plt.tight_layout()
plt.savefig('output/monthly_sales_trend.png')
print("\n[Chart Generated] output/monthly_sales_trend.png")

# 2. Top 10 Items Bar Chart
top_10_items = item_popularity.head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=top_10_items.values, y=top_10_items.index, palette='viridis')
plt.title('Top 10 Menu Items by Quantity Sold')
plt.xlabel('Quantity Sold')
plt.tight_layout()
plt.savefig('output/top_10_items.png')
print("[Chart Generated] output/top_10_items.png")

# --- Export Summary CSV ---
# Creating a simple summary dataframe for export
summary_data = {
    'Metric': ['Total Unique Items', 'Total Orders', 'Total Items Sold', 'Max Order Quantity', 'Total Revenue'],
    'Value': [num_unique_items, total_orders, total_items_sold, largest_order_qty, df['total_line_price'].sum()]
}
pd.DataFrame(summary_data).to_csv('output/analysis_summary.csv', index=False)
print("[CSV Exported] output/analysis_summary.csv")

print("--- ANALYSIS COMPLETE ---")
