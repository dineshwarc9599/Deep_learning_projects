import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="Demand Forecasting", layout="wide")

# ---------------------------------------------------
# LOAD MODEL FILES
# ---------------------------------------------------

model = joblib.load("demand_model.pkl")
feature_cols = joblib.load("feature_cols.pkl")
encoders = joblib.load("encoders.pkl")

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("📊 Apparel Demand Forecasting")
st.write("Predict weekly demand for apparel SKU attributes")

# ---------------------------------------------------
# USER INPUT SECTION
# ---------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    department = st.selectbox(
        "Department",
        ["KNIT TOP SETS", "WOVEN TOP SETS"]
    )

    sleeve = st.selectbox(
        "Sleeve",
        ["FULL", "HALF", "SLEEVELESS"]
    )

with col2:
    length = st.selectbox(
        "Length",
        ["SHORT", "LONG"]
    )

    range_val = st.selectbox(
        "Range",
        ["LOW", "MID", "HIGH"]
    )

with col3:
    size = st.selectbox(
        "Size",
        ["S", "M", "L", "XL"]
    )

    warehouse = st.text_input("Warehouse Code")

# ---------------------------------------------------
# PRICE SECTION
# ---------------------------------------------------

st.subheader("💰 Pricing Information")

col4, col5 = st.columns(2)

with col4:
    mrp = st.number_input("MRP", min_value=0.0)

with col5:
    discount_pct = st.slider("Discount %", 0.0, 1.0, 0.0)

# ---------------------------------------------------
# DATE SECTION
# ---------------------------------------------------

st.subheader("📅 Time Information")

col6, col7 = st.columns(2)

with col6:
    week_date = st.date_input("Week Start Date")

with col7:
    product_age = st.number_input("Product Age (weeks)", min_value=0)

# ---------------------------------------------------
# PREDICTION BUTTON
# ---------------------------------------------------

if st.button("🚀 Predict Demand"):

    try:

        date = pd.to_datetime(week_date)

        week = date.isocalendar().week
        month = date.month
        day_of_week = date.dayofweek
        quarter = date.quarter

        # ---------------------------------------------------
        # BUILD FEATURE ROW
        # ---------------------------------------------------

        row = {}

        row["mrp"] = mrp
        row["discount_pct"] = discount_pct
        row["month"] = month
        row["week"] = week
        row["quarter"] = quarter
        row["day_of_week"] = day_of_week
        row["is_weekend"] = int(day_of_week >= 5)
        row["product_age_week"] = product_age

        # ---------------------------------------------------
        # ENCODE CATEGORICAL FEATURES
        # ---------------------------------------------------

        row["department_enc"] = encoders["department"].transform([department])[0]
        row["sleeve_enc"] = encoders["sleeve"].transform([sleeve])[0]
        row["length_enc"] = encoders["length"].transform([length])[0]
        row["range_enc"] = encoders["range"].transform([range_val])[0]
        row["size_enc"] = encoders["size"].transform([size])[0]
        row["warehouse_code_enc"] = encoders["warehouse_code"].transform([warehouse])[0]

        # ---------------------------------------------------
        # HANDLE MISSING FEATURES
        # ---------------------------------------------------

        for col in feature_cols:
            if col not in row:
                row[col] = 0

        X = pd.DataFrame([row])[feature_cols]

        # ---------------------------------------------------
        # MODEL PREDICTION
        # ---------------------------------------------------

        prediction = model.predict(X)[0]

        expected_demand = round(prediction, 2)
        recommended_stock = int(np.ceil(prediction))

        # ---------------------------------------------------
        # OUTPUT
        # ---------------------------------------------------

        st.subheader("📈 Forecast Result")

        col8, col9 = st.columns(2)

        with col8:
            st.metric("Expected Demand", f"{expected_demand} units")

        with col9:
            st.metric("Recommended Stock", f"{recommended_stock} units")

        st.success("Prediction completed successfully")

    except Exception as e:
        st.error(f"Error during prediction: {e}")