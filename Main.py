import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# Function to parse the input data into a DataFrame
def parse_input_data(input_data):
    data = [line.split() for line in input_data.strip().split('\n')]
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.apply(pd.to_numeric, errors='coerce')
    return df

# Standard axis data
rpm_values = np.array([650, 800, 992, 1248, 1500, 1750, 2016, 2496, 3008, 3488, 4000, 4512, 4992, 5504, 6016, 6592])

st.title('ECU Tuning Map Adjustments')

# Step 1: Input the indicated torque
st.write('Step 1: Paste the indicated torque data.')
indicated_torque_input = st.text_area("Indicated Torque (Paste Data)")

# Step 2: Input the stock boost level
st.write('Step 2: Input the stock boost level.')
stock_boost = st.number_input("Stock Boost Level (PSI)", value=16.0)

# Step 3: Input the inverse maps
st.write('Step 3: Paste the two inverse maps.')

mass_airflow_inverse_input = st.text_area("Mass Airflow (Inverse) (Paste Data)")
reference_torque_inverse_input = st.text_area("Reference Torque (Inverse) (Paste Data)")

# Step 4: Input new desired max torque at WOT and boost pressure target
st.write('Step 4: Input the new desired max torque at WOT and boost pressure target.')

new_max_torque = st.number_input("New Max Torque at WOT (Nm)", value=630.0)
new_boost_target = st.number_input("New Boost Pressure Target (PSI)", value=20.0)

# Step 5: Analyze and generate new maps
if indicated_torque_input and mass_airflow_inverse_input and reference_torque_inverse_input:
    indicated_torque_df = parse_input_data(indicated_torque_input)
    mass_airflow_inverse_df = parse_input_data(mass_airflow_inverse_input)
    reference_torque_inverse_df = parse_input_data(reference_torque_inverse_input)

    # Ensure all data is numeric
    indicated_torque_df = indicated_torque_df.apply(pd.to_numeric, errors='coerce').fillna(0)
    mass_airflow_inverse_df = mass_airflow_inverse_df.apply(pd.to_numeric, errors='coerce').fillna(0)
    reference_torque_inverse_df = reference_torque_inverse_df.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Calculate the torque increase factor
    stock_max_torque = indicated_torque_df.max().max()  # Assuming the max value in the indicated torque is the stock max torque
    torque_increase_factor = new_max_torque / stock_max_torque

    # Calculate the boost increase factor
    boost_increase_factor = new_boost_target / stock_boost

    # Generate new indicated torque and mass airflow inverse tables
    new_indicated_torque_df = indicated_torque_df * torque_increase_factor
    new_mass_airflow_inverse_df = mass_airflow_inverse_df * boost_increase_factor

    # Display the new tables
    st.write('New Indicated Torque Table:')
    st.dataframe(new_indicated_torque_df)

    st.write('New Mass Airflow (Inverse) Table:')
    st.dataframe(new_mass_airflow_inverse_df)

    # Function to format DataFrame for easy copy-pasting
    def format_for_copy_paste(df):
        return df.to_csv(sep='\t', index=False)

    # Provide download buttons for the new tables
    st.download_button(
        label="Download New Indicated Torque Table",
        data=format_for_copy_paste(new_indicated_torque_df),
        file_name='new_indicated_torque_table.csv',
        mime='text/csv'
    )

    st.download_button(
        label="Download New Mass Airflow (Inverse) Table",
        data=format_for_copy_paste(new_mass_airflow_inverse_df),
        file_name='new_mass_airflow_inverse_table.csv',
        mime='text/csv'
    )
