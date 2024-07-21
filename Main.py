import streamlit as st
import pandas as pd
import numpy as np

# Step 1: Create a downloadable CSV template
def create_template():
    template_data = {
        "RPM": ["650", "800", "992", "1248", "1500", "1750", "2016", "2496", "3008", "3488", "4000", "4512", "4992", "5504", "6016", "6592"],
        "0": ["0"] * 16,
        "25": [""] * 16,
        "50": [""] * 16,
        "100": [""] * 16,
        "150": [""] * 16,
        "200": [""] * 16,
        "250": [""] * 16,
        "300": [""] * 16,
        "350": [""] * 16,
        "400": [""] * 16,
        "450": [""] * 16,
        "500": [""] * 16
    }
    df_template = pd.DataFrame(template_data)
    df_template.to_csv('template.csv', index=False)

# Step 2: Streamlit app
def main():
    st.title("ECU Map Rescaler")

    # Download the template
    st.header("Step 1: Download the CSV Template")
    create_template()
    with open("template.csv", "rb") as file:
        st.download_button(label="Download CSV Template", data=file, file_name="template.csv", mime="text/csv")

    # Upload the filled template
    st.header("Step 2: Upload the Filled CSV Template")
    uploaded_file = st.file_uploader("Upload your filled template", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("### Original Map")
        st.dataframe(df)

        # Convert to numeric values
        df = df.apply(pd.to_numeric, errors='coerce')

        # Extract RPM values and torque axis
        rpm_values = df.iloc[0, 1:].values
        torque_axis = df.iloc[1:, 0].values
        airflow_data = df.iloc[1:, 1:].values

        # Calculate airflow per torque factor
        airflow_per_torque = airflow_data / torque_axis[:, np.newaxis]

        # Ask for new torque axis
        st.header("Step 3: Input New Torque Axis")
        new_torque_axis_input = st.text_area("Enter new torque axis values (one value per line)", "30\n60\n90\n120\n150")
        new_torque_axis = [int(torque.strip()) for torque in new_torque_axis_input.split("\n")]

        if st.button("Generate New Map"):
            # Calculate new airflow values using the new torque axis
            new_airflow_values = airflow_per_torque * np.array(new_torque_axis)[:, np.newaxis]

            # Create a DataFrame to display the results
            result_df = pd.DataFrame(new_airflow_values, columns=df.columns[1:], index=new_torque_axis)
            result_df.index.name = "Torque (Nm)"
            st.write("### New Airflow Map")
            st.dataframe(result_df)

            # Provide option to download the new map as a CSV
            csv = result_df.to_csv().encode('utf-8')
            st.download_button(label="Download New Airflow Map as CSV", data=csv, file_name='new_airflow_map.csv', mime='text/csv')

if __name__ == "__main__":
    main()
