import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import io

def preprocess_data(df):
    # Handle NaNs and convert data types
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.fillna(method='ffill').fillna(method='bfill')
    return df

def load_data(file):
    xls = pd.ExcelFile(file)
    sheets = xls.sheet_names
    data = {sheet: preprocess_data(pd.read_excel(xls, sheet_name=sheet)) for sheet in sheets}
    return data

def train_model(data):
    X = []
    y = []
    for sheet, df in data.items():
        x_values = df.iloc[:, 0].values
        y_values = df.columns[1:].astype(float)
        for i, x in enumerate(x_values):
            for j, y_val in enumerate(y_values):
                X.append([x, y_val])
                y.append(df.iloc[i, j + 1])
    X = np.array(X)
    y = np.array(y)
    model = RandomForestRegressor(n_estimators=100, random_state=0)
    model.fit(X, y)
    return model

def interpolate(model, x_range, y_values):
    new_X = np.array([[x, y] for x in x_range for y in y_values])
    new_y = model.predict(new_X)
    interpolated_values = new_y.reshape(len(x_range), len(y_values))
    return interpolated_values

def create_template():
    columns = ["Torque (Nm)"] + [f"RPM {i}" for i in range(1, 11)]
    data = [[i*10 for i in range(11)] for _ in range(10)]
    df_template = pd.DataFrame(data, columns=columns)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

st.title("3D Table Interpolation App")

# Provide a downloadable template
st.download_button(
    label="Download Template",
    data=create_template(),
    file_name="3D_Table_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")
if uploaded_file is not None:
    data = load_data(uploaded_file)
    st.write("Sheets loaded:", list(data.keys()))
    
    axis_label = st.selectbox("Select the axis to expand", ["Torque (Nm)", "Airflow"])
    new_scale = st.number_input(f"Expand {axis_label} to", min_value=0, max_value=1000, value=650, step=1)
    
    model = train_model(data)
    
    sample_sheet = next(iter(data.values()))
    y_values = sample_sheet.columns[1:].astype(float)
    x_range = np.linspace(sample_sheet.iloc[:, 0].min(), new_scale, num=sample_sheet.shape[0] + 1)
    
    interpolated_values = interpolate(model, x_range, y_values)
    
    df_interpolated = pd.DataFrame(interpolated_values, columns=y_values)
    df_interpolated.insert(0, axis_label, x_range)
    
    st.write(f"Interpolated 3D Table for {axis_label}")
    st.dataframe(df_interpolated)
    
    # Convert dataframe to excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_interpolated.to_excel(writer, index=False, sheet_name='Interpolated Data')
    processed_data = output.getvalue()
    
    st.download_button(
        label="Download Interpolated Table",
        data=processed_data,
        file_name="Interpolated_Mass_Airflow.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
