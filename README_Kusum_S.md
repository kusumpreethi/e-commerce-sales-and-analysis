# 🛒 E-COMMERCE SALES AND ANALYSIS - Project

## 📌 Objective
Convert messy 50K dataset (12 cols) to clean dashboard dataset (15 cols) using Python and visualize with Power BI dark theme.

**Live Dashboard:** Host the HTML artifact on GitHub Pages

## 📊 Before vs After

| Aspect | Messy | Cleaned |
|--------|-------|---------|
| Rows | 50,000 | 50,000 |
| Cols | 12 | 15 |
| Sales | Unreliable | ₹152.43 Cr |
| Profit | Unreliable | ₹24.33 Cr (15.96% margin) |

## 🧹 Cleaning Steps with Python Syntax

### Step 1: Import Libraries
```python
import pandas as pd
import numpy as np
```

### Step 2: Load Data
```python
df = pd.read_excel("Data_Analyst_Dataset_50000_Rows.xlsx", sheet_name="Sheet")
print(df.shape)  # (50000, 12)
```

### Step 3: Product Master (Key Fix - 40% margin)
```python
product_master = {
    'Table': {'purchase': 2000, 'sales': 2800},
    'Desk': {'purchase': 3500, 'sales': 4900},
    'Chair': {'purchase': 3000, 'sales': 4200},
    'Keyboard': {'purchase': 2250, 'sales': 3150},
    'Mouse': {'purchase': 375, 'sales': 525},
    'Laptop': {'purchase': 30000, 'sales': 42000},
    'Notebook': {'purchase': 300, 'sales': 420},
    'Paper': {'purchase': 450, 'sales': 630},
    'Pen': {'purchase': 100, 'sales': 140},
}
df['Purchase Price'] = df['Product'].map(lambda x: product_master.get(x, {}).get('purchase'))
df['Sales Unit Price'] = df['Product'].map(lambda x: product_master.get(x, {}).get('sales'))
```

### Step 4: Column Standardization
```python
df.rename(columns={'OrderID': 'Order_id'}, inplace=True)
```

### Step 5: Date Cleaning
```python
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
```

### Step 6: Text Cleaning
```python
for col in ['Customer', 'City', 'Category', 'Product', 'Payment']:
    df[col] = df[col].astype(str).str.strip().str.title()

payment_map = {'Card': 'Card', 'Cash': 'Cash', 'Netbanking': 'NetBanking', 'Upi': 'UPI'}
df['Payment'] = df['Payment'].map(lambda x: payment_map.get(x, x))
```

### Step 7: Numeric Cleaning
```python
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(1).astype(int)
df['Quantity'] = df['Quantity'].clip(lower=1, upper=10)

df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce').fillna(0)
df['Discount %'] = np.where(df['Discount'] <= 1, df['Discount']*100, df['Discount'])
df['Discount %'] = df['Discount %'].round(0).astype(int).clip(0, 30)
```

### Step 8: Calculate Correct Business Logic (CORE)
```python
df['Total Purchase Price'] = df['Purchase Price'] * df['Quantity']
df['Total amount'] = df['Sales Unit Price'] * df['Quantity']
df['Grand Total'] = df['Total amount'] * (1 - df['Discount %']/100)
df['Profit'] = df['Grand Total'] - df['Total Purchase Price']
```

### Step 9: Final Formatting & Export
```python
final_cols = ['Order_id', 'Date', 'Customer', 'City', 'Category', 'Product',
              'Purchase Price', 'Quantity', 'Total Purchase Price',
              'Sales Unit Price', 'Total amount', 'Discount %',
              'Grand Total', 'Profit', 'Payment']
clean_df = df[final_cols].sort_values('Order_id')
clean_df.drop_duplicates(inplace=True)
clean_df.to_excel("Project-Cleaned-Dataset-Final.xlsx", index=False)
```

## 📈 Dashboard Design (Like Your Screenshots)

### Page 1 - KPI Cards
- Total sales: 1.52bn = SUM(Grand Total)
- Total quantity: 276K = SUM(Quantity)
- Total profit: 243.32M = SUM(Profit)
- Total orders: 50K = COUNT(Order_id)

Visuals: Sales by Product (Donut - Laptop 71%), Profit by Category (Bar), Profit by City (H-Bar), Sales by Payment (Donut), Quantity vs Profit (Scatter), Sales by Year (Line 771M→753M)

### Page 2
Profit by Product (Bar - Laptop 173M), India Map (5 cities), Sales by Month (Line), Quantity by Product (H-Bar)

## 🚀 DAX Measures (Power BI)

```DAX
Total Sales = SUM('Clean_Data'[Grand Total])
Total Profit = SUM('Clean_Data'[Profit])
Profit Margin % = DIVIDE([Total Profit], [Total Sales], 0) * 100
Total Orders = COUNT('Clean_Data'[Order_id])
AOV = DIVIDE([Total Sales], [Total Orders], 0)

Sales YoY Growth = 
 VAR Curr = [Total Sales]
 VAR Prev = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Clean_Data'[Date]))
 RETURN DIVIDE(Curr-Prev, Prev, 0)
```

## 💻 Run Locally
```bash
pip install -r requirements.txt
python src/data_cleaning.py
streamlit run src/dashboard_app.py
```

## 📂 Structure
```
data/ - messy + cleaned xlsx
src/ - data_cleaning.py, dashboard_app.py
images/ - page1.png, page2.png
README.md
```

## Key Insights
1. Laptop 71% sales (108Cr) & profit (17.32Cr)
2. Electronics 77% of profit
3. City balanced: Bengaluru 4.95Cr top
4. 2024→2025 -2.3% decline

Author: Kusum S | Chennai
