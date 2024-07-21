import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# Load Excel file
file_path = 'CN7N TQI and Airflow Workbook.xlsx'
xls = pd.ExcelFile(file_path)

# Load necessary sheets
indicated_torque_df = pd.read_excel(xls, 'Indicated Torque at Reference')
stock_torque_df = pd.read_excel(xls, 'Stock Torque')
air_mass_max_df = pd.read_excel(xls, 'Air Mass Max')
mass_airflow_inverse_df = pd.read_excel(xls, 'Mass Airflow (Inverse)')
reference_torque_inverse_df = pd.read_excel(xls, 'Reference Torque (Inverse)')

# User inputs for new targets
st.title('ECU Tuning Map Adjustments')
st.write('Input your desired boost level and torque targets over the RPM range.')

boost_level = st.number_input('Enter desired boost level (PSI)', value=16)
torque_target_1500 = st.number_input('Torque at 1500 RPM (Nm)', value=298.28)
torque_target_2000 = st.number_input('Torque at 2000 RPM (Nm)', value=318.62)
torque_target_2500 = st.number_input('Torque at 2500 RPM (Nm)', value=332.18)
torque_target_3000 = st.number_input('Torque at 3000 RPM (Nm)', value=338.95)
torque_target_3500 = st.number_input('Torque at 3500 RPM (Nm)', value=345.73)
torque_target_4000 = st.number_input('Torque at 4000 RPM (Nm)', value=352.51)
torque_target_4500 = st.number_input('Torque at 4500 RPM (Nm)', value=349.80)
torque_target_5000 = st.number_input('Torque at 5000 RPM (Nm)', value=345.73)
torque_target_5500 = st.number_input('Torque at 5500 RPM (Nm)', value=336.24)
torque_target_6000 = st.number_input('Torque at 6000 RPM (Nm)', value=325.40)
torque_target_6500 = st.number_input('Torque at 6500 RPM (Nm)', value=298.28)

# Create new torque target array
new_torque_targets = np.array([
    torque_target_1500, torque_target_2000, torque_target_2500,
    torque_target_3000, torque_target_3500, torque_target_4000,
    torque_target_4500, torque_target_5000, torque_target_5500,
    torque_target_6000, torque_target_6500
])

rpm_values = np.array([1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500])

# Interpolate and extrapolate new airflow values
def interpolate_airflow(new_torque_targets, stock_torque_df, air_mass_max_df):
    stock_rpm = stock_torque_df['RPM'].values
    stock_torque = stock_torque_df['Torque (Nm)'].values
    interp_func = interp1d(stock_rpm, stock_torque, kind='linear', fill_value='extrapolate')
    adjusted_torque = interp_func(rpm_values)

    air_mass_values = air_mass_max_df.iloc[:, 1:].values
    new_air_mass_values = np.zeros_like(air_mass_values)

    for i, rpm in enumerate(rpm_values):
        air_mass_interp_func = interp1d(stock_torque, air_mass_values[i], kind='linear', fill_value='extrapolate')
        new_air_mass_values[i] = air_mass_interp_func(new_torque_targets[i])

    return new_air_mass_values

new_air_mass_values = interpolate_airflow(new_torque_targets, stock_torque_df, air_mass_max_df)

# Display new tables
st.write('New Air Mass Table:')
new_air_mass_df = pd.DataFrame(new_air_mass_values, index=rpm_values, columns=air_mass_max_df.columns[1:])
st.write(new_air_mass_df)

# Save the new maps to CSV (if needed)
st.download_button(label="Download New Air Mass Table as CSV", data=new_air_mass_df.to_csv().encode('utf-8'), file_name='new_air_mass_table.csv', mime='text/csv')
