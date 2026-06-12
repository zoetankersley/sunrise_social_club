import pandas as pd
import os

sales = pd.read_csv('data/raw/item_sales_may.csv')
weather = pd.read_csv('data/external/weather.csv')
events = pd.read_csv('data/external/events.csv')

sales.columns = sales.columns.str.strip().str.replace(" ", "_")
weather.columns = weather.columns.str.strip().str.replace(" ", "_")
events.columns = events.columns.str.strip().str.replace(" ", "_")

sales['Date'] = pd.to_datetime(sales['Date'])
weather['Date'] = pd.to_datetime(weather['Date'])
events['Date'] = pd.to_datetime(events['Date'])

sales = sales.drop(columns=["Event_Type"], errors="ignore")

# Merge sales with weather data
df = sales.merge(weather, on='Date', how='left')
# Merge the resulting dataframe with events data
df = df.merge(events, on='Date', how='left')


df.columns = df.columns.str.strip().str.replace(" ", "_")

money_cols = ["Net_Sales", "Gross_Sales", "Tax", "Discounts"]

for col in money_cols:
    if col in df.columns:
        df[col] = (
            df[col]
            .replace(r"[\$,]", "", regex=True)
            .replace(r"^\((.*)\)$", r"-\1", regex=True)
            .astype(float)
        )

df = df.drop(columns=["Location_x"], errors="ignore")
df = df.rename(columns={"Location_y": "Location"})

keep_cols = [
    "Date",
    "Item",
    "Qty",
    "Net_Sales",
    "Modifiers_Applied",
    "Avg_Temp",
    "Weather_Condition",
    "Event_Type",
    "Location",
    "Time"
]

df = df[keep_cols]

# Ensure output directory exists and save the final dataset
import os
os.makedirs('data/processed', exist_ok=True)
df.to_csv('data/processed/sales_may_merged.csv', index=False)
print('Dataset built successfully!')
print(df.head())
