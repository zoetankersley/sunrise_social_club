import pandas as pd
import os

import glob
sales = pd.concat([pd.read_csv(f) for f in glob.glob("data/raw/*.csv")])
weather = pd.read_csv('data/external/weather.csv')
events = pd.read_csv('data/external/events.csv')

sales.columns = sales.columns.str.strip().str.replace(" ", "_")
weather.columns = weather.columns.str.strip().str.replace(" ", "_")
events.columns = events.columns.str.strip().str.replace(" ", "_")

sales["Item"] = (
    sales["Item"]
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.title()
)
sales = sales[sales["Item"] != "Custom Amount"]
sales["Original_Item"] = sales["Item"]

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

def parse_modifiers(x):
    if pd.isna(x):
        return pd.Series([None, None, None])
    
    parts = [p.strip() for p in str(x).split(",")]

    size = None
    milk = None
    addons = []

    for p in parts:
        if "oz" in p:
            size = p
        elif "Milk" in p:
            milk = p
        else:
            addons.append(p)

    return pd.Series([size, milk, ", ".join(addons) if addons else None])


df[["Size", "Milk", "Addons"]] = df["Modifiers_Applied"].apply(parse_modifiers)

def split_addons(x):
    if pd.isna(x):
        return pd.Series([0, None])

    parts = [p.strip().title() for p in x.split(",")]

    cold_foam = 1 if "Cold Foam" in parts else 0

    flavors = [
        p for p in parts
        if p not in ["Cold Foam", "Sprinkles!", "Lemonade"]
    ]

    return pd.Series([
        cold_foam,
        ", ".join(flavors) if flavors else None
    ])

df[["Cold_Foam", "Flavor"]] = df["Addons"].apply(split_addons)

df["Base"]=df["Milk"]
df.loc[df['Item']=="Lemonade", "Base"] = "Lemonade"

mask=((df['Item']=="Matcha Latte") & (df['Flavor'].fillna("").str.contains('Lemonade', case=False))) | ((df['Item']=="Iced Coffee") & (df['Flavor'].fillna("").str.contains('Lemonade', case=False)))
df.loc[mask, "Base"] = "Lemonade"

df.loc[mask, "Flavor"] = (
    df.loc[mask, "Flavor"]
      .str.replace("Lemonade", "", regex=False)
      .str.replace(", ,", ",")
      .str.strip(", ")
)

df['Signature_Drink']= df["Original_Item"].isin(["Ashlen", "Aaron", "Maple Pancakes", "Lemon Dream"])

special_drinks = {
    "Ashlen": {
        "Item": "Matcha Latte",
        "Base": "Lemonade",
        "Flavor": "Strawberry",
        "Cold_Foam": 0
    },
    "Aaron": {
        "Item": "Lemonade",
        "Base": "Lemonade",
        "Flavor": "Strawberry, Blueberry",
        "Cold_Foam": 0
    },
    "Maple Pancakes": {
        "Item": "Matcha Latte",
        "Base": "Whole Milk",
        "Flavor": "Salted Maple",
        "Cold_Foam": 1
    },
    "Lemon Dream": {
        "Item": "Matcha Latte",
        "Base": "Lemonade",
        "Flavor": "No Syrup",
        "Cold_Foam": 1
    }
}


for drink, attrs in special_drinks.items():
    mask = df["Original_Item"] == drink

    df.loc[mask, "Item"] = attrs["Item"]
    df.loc[mask, "Base"] = attrs["Base"]
    df.loc[mask, "Flavor"] = attrs["Flavor"]
    df.loc[mask, "Cold_Foam"] = attrs["Cold_Foam"]


keep_cols = [
    "Date",
    "Time",
    "Original_Item",
    "Item",
    "Base",
    "Signature_Drink",
    "Qty",
    "Net_Sales",
    "Size",
    "Cold_Foam",
    "Flavor",
    "Avg_Temp",
    "Weather_Condition",
    "Event_Type",
    "Location"
]

df = df[keep_cols]

# Ensure output directory exists and save the final dataset
import os
os.makedirs('data/processed', exist_ok=True)
df.to_csv('data/processed/sales_merged.csv', index=False)
print('Dataset built successfully!')
print(df.head())
