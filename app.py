import streamlit as st
import pandas as pd
import numpy as np
import pickle

import joblib

rf = joblib.load("rf_model.pkl")
X_columns = joblib.load("model_columns.pkl")

st.title("☕ Sunrise Social Club Demand Predictor")

st.write("Predict drink demand based on event conditions.")

# User Inputs
location = st.selectbox("Location", ["Manteo", "First Flight", "Soundside"])
event_type = st.selectbox("Event Type", ["Market", "Popup", "Private"])
avg_temp = st.slider("Average Temperature (°F)", 50, 100, 80)
day_of_week = st.selectbox(
    "Day of Week",
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
)
month = st.slider("Month", 1, 12, 6)

def build_input():
    items = ["Matcha Latte", "Cold Brew", "Lemonade"]
    flavors = ['Strawberry','Blueberry','Salted Maple','Banana','Cinn Roll','Vanilla','Cake Batter']

    rows = []

    for item in items:
        for flavor in flavors:
            rows.append({
                "Item": item,
                "Flavor": flavor,
                "Location": location,
                "Event_Type": event_type,
                "Avg_Temp": avg_temp,
                "Day_of_Week": day_of_week,
                "Month": month,
                "Weekend": day_of_week in ["Saturday", "Sunday"]
            })

    return pd.DataFrame(rows)


def preprocess(df_input):
    df_encoded = pd.get_dummies(df_input)
    df_encoded = df_encoded.reindex(columns=X_columns, fill_value=0)
    return df_encoded

if st.button("Predict Demand"):

    input_df = build_input()
    encoded = preprocess(input_df)

    input_df["Predicted_Qty"] = rf.predict(encoded)

    st.subheader("Predicted Demand by Item + Flavor")
    st.dataframe(input_df)

    # Aggregate by Item
    st.subheader("Total Demand by Item")

    item_totals = input_df.groupby("Item")["Predicted_Qty"].sum()

    st.bar_chart(item_totals)

    # Aggregate by Flavor
    st.subheader("Total Demand by Flavor")

    flavor_totals = input_df.groupby("Flavor")["Predicted_Qty"].sum()

    st.bar_chart(flavor_totals)