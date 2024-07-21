import streamlit as st
import pandas as pd
import numpy as np

# Step 1: Create a downloadable combined CSV template
def create_combined_template():
    template_data1 = {
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
    df_template1 = pd.DataFrame(template_data1)
    
    template_data2 = {
        "Reference Torque (Nm)": ["50.02", "99.997", "199.994", "299.991", "399.013", "499.01", "599.007", "702.014", "800.018", "1000.012", "1200.006", "1400"],
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
    df_template2 = pd.DataFrame(template_data2)
    
    with open('combined_template.csv', 'w') as f:
        f.write('Airflow Map\n')
        df_template1.to_csv(f, index=False)
        f.write('\nReference Torque Map\n')
        df_template2.to_csv(f, index=False)

# Step 2: Streamlit app
def main():
    st.title("ECU Map Rescaler")

    # Download the template
    st.header("Step 1: Download the Combined CSV Template")
    create_combined_template()
    with open("combined_template.csv", "rb") as file:
        st.download_button(label="Download Combined CSV Template", data=file, file_name="combined_template.csv", mime="text/csv")

    # Upload the filled template
    st.header("Step 2: Upload the Filled Combined CSV Template")
    uploaded_file = st.file_uploader("Upload your filled combined template", type="csv")

    if uploaded_file is not None:
        # Read the combined CSV and split into two DataFrames
        combined_df = pd.read_csv(uploaded_file, skip_blank_lines=False, header=None)
        
        # Locate the split point
        split_idx = combined_df[combined_df[0].str.contains("Reference Torque Map", na=False)].index[0]

        # Extract the two maps
        airflow_df = pd.read_csv(uploaded_file, skiprows=1, nrows=split_idx-2)
        reference_torque_df = pd.read_csv(uploaded_file, skiprows=split_idx+1)

        st.write("### Original Airflow Map")
        st.dataframe(airflow_df)

        st.write("### Original Reference Torque Map")
        st.dataframe(reference_torque_df)

        # Convert to numeric values
        airflow_df = airflow_df.apply(pd.to_numeric, errors='coerce')
        reference_torque_df = reference_torque_df.apply(pd.to_numeric, errors='coerce')

        # Extract torque values and RPM axis for airflow map
        torque_axis1 = airflow_df.iloc[:, 0].values
        rpm_values1 = airflow_df.columns[1:].astype(int)
        airflow_data = airflow_df.iloc[:, 1:].values

        # Calculate airflow per torque factor
        with np.errstate(divide='ignore', invalid='ignore'):
            airflow_per_torque = np.where(torque_axis1[:, np.newaxis] != 0, airflow_data / torque_axis1[:, np.newaxis], 0)

        # Display the extracted torque axis as a text area
        st.header("Step 3: Input New Torque Axis for Airflow Map")
        st.write("The values below are extracted from the uploaded template. You can edit them if needed.")
        
        torque_axis_str1 = "\n".join(map(str, torque_axis1))
        new_torque_axis_input1 = st.text_area("New Torque Axis (one value per line)", torque_axis_str1)
        new_torque_axis1 = [int(torque.strip()) for torque in new_torque_axis_input1.split("\n")]

        if st.button("Generate New Maps"):
            # Calculate new airflow values using the new torque axis
            new_airflow_values = airflow_per_torque * np.array(new_torque_axis1)[:, np.newaxis]

            # Create a DataFrame to display the results
            result_df1 = pd.DataFrame(new_airflow_values, columns=airflow_df.columns[1:], index=new_torque_axis1)
            result_df1.index.name = "Torque (Nm)"

            st.write("### New Airflow Map")
            st.dataframe(result_df1)

            # Provide option to download the new map as a CSV
            csv1 = result_df1.to_csv().encode('utf-8')
            st.download_button(label="Download New Airflow Map as CSV", data=csv1, file_name='new_airflow_map.csv', mime='text/csv')

            # Proceed with the second map
            # Extract reference torque values and RPM axis
            reference_torque_axis = reference_torque_df.iloc[:, 0].values
            rpm_values2 = reference_torque_df.columns[1:].astype(int)
            reference_torque_data = reference_torque_df.iloc[:, 1:].values

            # Calculate reference torque per factor
            with np.errstate(divide='ignore', invalid='ignore'):
                reference_torque_per_factor = np.where(reference_torque_axis[:, np.newaxis] != 0, reference_torque_data / reference_torque_axis[:, np.newaxis], 0)

            # Generate new reference torque axis
            new_reference_torque_axis = [50] + [np.mean(result_df1.iloc[i]) for i in range(1, len(result_df1))]

            # Calculate new reference torque values using the new torque axis
            new_reference_torque_values = reference_torque_per_factor * np.array(new_reference_torque_axis)[:, np.newaxis]

            # Create a DataFrame to display the results
            result_df2 = pd.DataFrame(new_reference_torque_values, columns=reference_torque_df.columns[1:], index=new_reference_torque_axis)
            result_df2.index.name = "Reference Torque (Nm)"

            st.write("### New Reference Torque Map")
            st.dataframe(result_df2)

            # Provide option to download the new map as a CSV
            csv2 = result_df2.to_csv().encode('utf-8')
            st.download_button(label="Download New Reference Torque Map as CSV", data=csv2, file_name='new_reference_torque_map.csv', mime='text/csv')

if __name__ == "__main__":
    main()
