import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# Load the Excel workbook
file_path = '/mnt/data/CN7N TQI and Airflow Workbook.xlsx'
xls = pd.ExcelFile(file_path)

# Load necessary sheets
indicated_torque_df = pd.read_excel(xls, 'Indicated Torque at Reference')
stock_torque_df = pd.read_excel(xls, 'Stock Torque')
air_mass_max_df = pd.read_excel(xls, 'Air Mass Max')
mass_airflow_inverse_df = pd.read_excel(xls, 'Mass Airflow (Inverse)')
reference_torque_inverse_df = pd.read_excel(xls, 'Reference Torque (Inverse)')

# Ensure proper data extraction and alignment
rpm_values_air_mass = air_mass_max_df.iloc[0].values[1:].astype(float)
air_mass_values = air_mass_max_df.iloc[1:].dropna().values.flatten().astype(float)  # Drop NaN and flatten to ensure proper shape

# Verify data shapes
(stock_rpm.shape, stock_torque.shape, air_mass_values.shape)

# Ensure the air mass values match the stock torque for interpolation
assert len(stock_torque) == len(air_mass_values), "Length mismatch between stock torque and air mass values"

# Set new target torque values for testing
new_torque_targets = np.array([298.28, 318.62, 332.18, 338.95, 345.73, 352.51, 349.80, 345.73, 336.24, 325.40, 298.28])
rpm_values = np.array([1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500])

# Function to interpolate and extend the map
def interpolate_airflow(new_torque_targets, stock_torque_df, air_mass_values, rpm_values_air_mass):
    stock_torque = stock_torque_df['Torque (Nm)'].values
    
    new_air_mass_values = np.zeros((len(rpm_values), len(rpm_values_air_mass)))
    
    for i, rpm in enumerate(rpm_values):
        air_mass_interp_func = interp1d(stock_torque, air_mass_values, kind='linear', fill_value='extrapolate')
        new_air_mass_values[i] = air_mass_interp_func(new_torque_targets)
    
    return new_air_mass_values

# Generate the new air mass map
new_air_mass_values = interpolate_airflow(new_torque_targets, stock_torque_df, air_mass_values, rpm_values_air_mass)

# Create DataFrame for the new air mass map
new_air_mass_df = pd.DataFrame(new_air_mass_values, index=rpm_values, columns=rpm_values_air_mass)

# Function to create inverse maps and indicated torque
def create_inverse_maps(new_air_mass_df, mass_airflow_inverse_df, reference_torque_inverse_df, new_torque_targets):
    mass_airflow_inverse_df = mass_airflow_inverse_df.copy()
    reference_torque_inverse_df = reference_torque_inverse_df.copy()

    for col in new_air_mass_df.columns:
        mass_airflow_inverse_df[col] = new_air_mass_df.loc[:, col].values
        reference_torque_inverse_df[col] = new_torque_targets

    return mass_airflow_inverse_df, reference_torque_inverse_df

# Create the inverse maps and indicated torque
new_mass_airflow_inverse_df, new_reference_torque_inverse_df = create_inverse_maps(new_air_mass_df, mass_airflow_inverse_df, reference_torque_inverse_df, new_torque_targets)

import ace_tools as tools; tools.display_dataframe_to_user(name="New Air Mass Map", dataframe=new_air_mass_df)
tools.display_dataframe_to_user(name="New Mass Airflow (Inverse) Table", dataframe=new_mass_airflow_inverse_df)
tools.display_dataframe_to_user(name="New Reference Torque (Inverse) Table", dataframe=new_reference_torque_inverse_df)

(new_air_mass_df, new_mass_airflow_inverse_df, new_reference_torque_inverse_df)
