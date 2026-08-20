
import pandas as pd
import numpy as np
from datetime import datetime

# 1. LOAD MESSY DATASET
INPUT_FILE = "/mnt/data/Data_Analyst_Dataset_50000_Rows.xlsx"
OUTPUT_FILE = "/mnt/data/Vishwa_Cleaned_Dataset_Final.xlsx"

df = pd.read_excel(INPUT_FILE, sheet_name="Sheet")
print(f"Original messy shape: {df.shape}")
print(df.head())

# 2. DEFINE PRODUCT MASTER (Purchase Price fixed for Vishwa Project)
# Based on your target dashboard file
product_master = {
    'Table':    {'purchase': 2000,  'sales': 2800},
    'Desk':     {'purchase': 3500,  'sales': 4900},
    'Chair':    {'purchase': 3000,  'sales': 4200},
    'Keyboard': {'purchase': 2250,  'sales': 3150},
    'Mouse':    {'purchase': 375,   'sales': 525},
    'Laptop':   {'purchase': 30000, 'sales': 42000},
    'Notebook': {'purchase': 300,   'sales': 420},
    'Paper':    {'purchase': 450,   'sales': 630},
    'Pen':      {'purchase': 100,   'sales': 140},
}

# Map to dataframe
df['Purchase Price'] = df['Product'].map(lambda x: product_master.get(x, {}).get('purchase'))
df['Sales Unit Price'] = df['Product'].map(lambda x: product_master.get(x, {}).get('sales'))

# 3. DATA CLEANING

# a) Standardize column names
df.rename(columns={'OrderID': 'Order_id'}, inplace=True)

# b) Clean Date - convert to datetime and sort
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
# Optional: If you want dashboard dates like target file (2024-01-01 to 2025-12-31 evenly)
# Comment this out if you want to keep original dates
# df = df.sort_values('Order_id')
# df['Date'] = pd.date_range(start='2024-01-01', end='2025-12-31', periods=len(df)).date

# c) Clean text fields - strip spaces, title case
for col in ['Customer', 'City', 'Category', 'Product', 'Payment']:
    df[col] = df[col].astype(str).str.strip().str.title()
    # Fix specific
    df[col] = df[col].replace({'Bengaluru': 'Bengaluru', 'Mumbai': 'Mumbai'}) 

# Standardize Payment - Map variations
payment_map = {
    'Card': 'Card',
    'Cash': 'Cash',
    'Netbanking': 'NetBanking',
    'Upi': 'UPI',
    'Credit Card': 'Card',  # if exists
    'Debit Card': 'Card'
}
df['Payment'] = df['Payment'].map(lambda x: payment_map.get(x, x))

# d) Fix numeric columns
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(1).astype(int)
df['Quantity'] = df['Quantity'].clip(lower=1, upper=10) # based on target 1-10

df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce').fillna(0)
# If Discount >1 it means already %, else decimal 0.26 = 26%
df['Discount %'] = np.where(df['Discount'] <= 1, df['Discount']*100, df['Discount'])
df['Discount %'] = df['Discount %'].round(0).astype(int)
df['Discount %'] = df['Discount %'].clip(0, 30) # target is 5-20% mostly, but allow 0-30

# 4. CALCULATE DASHBOARD COLUMNS (CORRECT FORMULAS)
df['Total Purchase Price'] = df['Purchase Price'] * df['Quantity']
df['Total amount'] = df['Sales Unit Price'] * df['Quantity']
df['Grand Total'] = df['Total amount'] * (1 - df['Discount %']/100)
df['Profit'] = df['Grand Total'] - df['Total Purchase Price']

# 5. FINAL COLUMN ORDER AS PER VISHWA DASHBOARD
final_cols = ['Order_id', 'Date', 'Customer', 'City', 'Category', 'Product',
              'Purchase Price', 'Quantity', 'Total Purchase Price',
              'Sales Unit Price', 'Total amount', 'Discount %',
              'Grand Total', 'Profit', 'Payment']

clean_df = df[final_cols].copy()

# Round financial columns
for col in ['Purchase Price', 'Total Purchase Price', 'Sales Unit Price', 'Total amount', 'Grand Total', 'Profit']:
    clean_df[col] = clean_df[col].round(2)

# Sort by Order_id
clean_df = clean_df.sort_values('Order_id')

# 6. VALIDATION & CLEANUP
clean_df.drop_duplicates(inplace=True)
clean_df.dropna(subset=['Order_id', 'Product'], inplace=True)

print(f"Cleaned shape: {clean_df.shape}")
print(clean_df.head(10))
print(clean_df.describe())

# 7. SAVE FOR DASHBOARD
clean_df.to_excel(OUTPUT_FILE, index=False, sheet_name='Clean_Data')
print(f"Saved cleaned file to: {OUTPUT_FILE}")

# Also create summary for dashboard verification
summary = clean_df.groupby(['Category', 'Product']).agg({
    'Quantity': 'sum',
    'Grand Total': 'sum',
    'Profit': 'sum'
}).reset_index()
print(summary)
summary.to_excel("/mnt/data/Vishwa_Dashboard_Summary.xlsx", index=False)
