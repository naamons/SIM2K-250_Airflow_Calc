import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# Streamlit UI
st.title('ECU Tuning Map Adjustments')
st.write('Upload your Excel file containing the necessary tables.')

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file:
    # Load the Excel workbook
    xls = pd.ExcelFile(uploaded_file)

    # Load necessary sheets
    indicated_torque_df = pd.read_excel(xls, 'Indicated Torque at Reference')
    stock_torque_df = pd.read_excel(xls, 'Stock Torque')
    air_mass_max_df = pd.read_excel(xls, 'Air Mass Max')
    mass_airflow_inverse_df = pd.read_excel(xls, 'Mass Airflow (Inverse)')
    reference_torque_inverse_df = pd.read_excel(xls, 'Reference Torque (Inverse)')

    # Extract RPM and air mass values correctly
    rpm_values_air_mass = air_mass_max_df.iloc[0, 1:].astype(float).values
    air_mass_values = air_mass_max_df.iloc[1:, 1:].values.flatten().astype(float)

    # Set default new target torque values
    default_new_torque_targets = np.array([298.28, 318.62, 332.18, 338.95, 345.73, 352.51, 349.80, 345.73, 336.24, 325.40, 298.28])
    rpm_values = np.array([1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500])

    st.write('Input your desired torque values over the RPM range.')

    # User inputs for new targets
    new_torque_targets = []
    for rpm in rpm_values:
        torque_value = st.number_input(f'Torque at {rpm} RPM (Nm)', value=float(default_new_torque_targets[list(rpm_values).index(rpm)]))
        new_torque_targets.append(torque_value)
    new_torque_targets = np.array(new_torque_targets)

    # Interpolate and extrapolate new airflow values
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

    st.write('New Air Mass Table:')
    st.dataframe(new_air_mass_df)

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

    st.write('New Mass Airflow (Inverse) Table:')
    st.dataframe(new_mass_airflow_inverse_df)

    st.write('New Reference Torque (Inverse) Table:')
    st.dataframe(new_reference_torque_inverse_df)

    # Function to format DataFrame for easy copy-pasting
    def format_for_copy_paste(df):
        return df.to_csv(sep='\t', index=False)

    # Provide download buttons for the new tables
    st.download_button(
        label="Download New Air Mass Table",
        data=format_for_copy_paste(new_air_mass_df),
        file_name='new_air_mass_table.csv',
        mime='text/csv'
    )

    st.download_button(
        label="Download New Mass Airflow (Inverse) Table",
        data=format_for_copy_paste(new_mass_airflow_inverse_df),
        file_name='new_mass_airflow_inverse_table.csv',
        mime='text/csv'
    )

    st.download_button(
        label="Download New Reference Torque (Inverse) Table",
        data=format_for_copy_paste(new_reference_torque_inverse_df),
        file_name='new_reference_torque_inverse_table.csv',
        mime='text/csv'
    )
