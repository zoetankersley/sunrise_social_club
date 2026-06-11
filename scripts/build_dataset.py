import pandas as pd

sales = pd.read_csv('data/raw/item_sales_may.csv')
weather = pd.read_csv('data/external/weather.csv')
events = pd.read_csv('data/external/events.csv')

sales['Date'] = pd.to_datetime(sales['Date'])
weather['Date'] = pd.to_datetime(weather['Date'])
events['Date'] = pd.to_datetime(events['Date'])

# Merge sales with weather data
df = sales.merge(weather, on='Date', how='left')
# Merge the resulting dataframe with events data
df = df.merge(events, on='Date', how='left')
 
# Fill missing values in the 'Event' column with 'No Event'
df["Event_Type"] = df["Event_Type"].fillna("None")

# Ensure output directory exists and save the final dataset
import os
os.makedirs('data/processed', exist_ok=True)
df.to_csv('data/processed/sales_may_merged.csv', index=False)
print('Dataset built successfully!')
print(df.head())
