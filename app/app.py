import streamlit as st
import pandas as pd
import joblib
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, "rf_model.pkl"))
model_columns = joblib.load(os.path.join(BASE_DIR, "model_columns.pkl"))

st.title("Sunrise Social Club Inventory Predictor")

event_type=st.selectbox('Event Type',['Market','Popup'])

location=st.selectbox('Location',['Manteo','First Flight','Soundside'])

month=st.slider('Month', min_value=1, max_value=12, value=6)

temp=st.slider('Average Temperature', min_value=0, max_value=100, value=70)

weather_condition=st.selectbox('Weather Condition',['Sunny','Cloudy','Partly Cloudy','Rainy'])

weekend=st.checkbox('Weekend Event?')

input_data = pd.DataFrame({'Event_Type':[event_type],
                           'Location':[location],
                            'Month':[month],
                           'Avg_Temp':[temp],
                           'Weather_Condition':[weather_condition],
                           'Weekend':[weekend]})

def build_event_grid(df):
    items = ["Matcha Latte", "Cold Brew", "Lemonade"]

    rows = []
    for item in items:
        temp_df = df.copy()
        temp_df["Item"] = item
        rows.append(temp_df)

    return pd.concat(rows, ignore_index=True)

grid = build_event_grid(input_data)
encoded = pd.get_dummies(grid)
encoded = encoded.reindex(columns=model_columns, fill_value=0)

grid['Predicted_Qty'] = model.predict(encoded)

# Inventory conversion
grams_12oz = {
    "Lemonade": 200,
    "Cold Brew": 100,
    "Matcha Latte": 40
}

grams_16oz = {
    "Lemonade": 275,
    "Cold Brew": 180,
    "Matcha Latte": 50
}

def compute_effective_grams():
    mix_16 = 0.8
    mix_12 = 0.2

    return {
        item: mix_16 * grams_16oz[item] + mix_12 * grams_12oz[item]
        for item in grams_12oz
    }

def inventory_calculator(df):
    effective = compute_effective_grams()
    GRAMS_PER_GALLON = 3300

    df["Grams"] = df.apply(
        lambda row: row["Predicted_Qty"] * effective[row["Item"]],
        axis=1
    )

    df["Gallons"] = df["Grams"] / GRAMS_PER_GALLON

    return df


result = inventory_calculator(grid)


st.subheader("Predicted Demand")
st.dataframe(result[["Item", "Predicted_Qty", "Gallons"]])

st.bar_chart(result.groupby("Item")["Gallons"].sum())