import streamlit as st
import pandas as pd
import numpy as np

# Step 1: Create a downloadable CSV template
def create_template():
    template_data = {
        "Torque (Nm)": ["0", "25", "50", "100", "150", "200", "250", "300", "350", "400", "450", "500"],
        "650": ["" for _ in range(12)],
        "800": ["" for _ in range(12)],
        "992": ["" for _ in range(12)],
        "1248": ["" for _ in range(12)],
        "1500": ["" for _ in range(12)],
        "1750": ["" for _ in range(12)],
        "2016": ["" for _ in range(12)],
        "2496": ["" for _ in range(12)],
        "3008": ["" for _ in range(12)],
        "3488": ["" for _ in range(12)],
        "4000": ["" for _ in range(12)],
        "4512": ["" for _ in range(12)],
        "4992": ["" for _ in range(12)],
        "5504": ["" for _ in range(12)],
        "6016": ["" for _ in range(12)],
        "6592": ["" for _ in range(12)]
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

        # Extract torque values and RPM axis
        torque_axis = df.iloc[:, 0].values
        rpm_values = df.columns[1:].astype(int)
        airflow_data = df.iloc[:, 1:].values

        # Calculate airflow per torque factor
        with np.errstate(divide='ignore', invalid='ignore'):
            airflow_per_torque = np.where(torque_axis[:, np.newaxis] != 0, airflow_data / torque_axis[:, np.newaxis], 0)

        # Display the extracted torque axis as a text area
        st.header("Step 3: Input New Torque Axis")
        st.write("The values below are extracted from the uploaded template. You can edit them if needed.")
        
        torque_axis_str = "\n".join(map(str, torque_axis))
        new_torque_axis_input = st.text_area("New Torque Axis (one value per line)", torque_axis_str)
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
