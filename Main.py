import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d

# Streamlit app
st.title("3D Table Adjuster")
st.write("Upload your Excel file with the table data.")

# File upload
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Read the Excel file
    try:
        df = pd.read_excel(uploaded_file, sheet_name=None)  # Reading all sheets

        # Assuming the sheet names are indicative of the data
        st.write("Sheets found:", list(df.keys()))

        # For simplicity, let's assume the first sheet contains the necessary data
        first_sheet_name = list(df.keys())[0]
        data_df = df[first_sheet_name]

        # Display the data
        st.write("Data from the first sheet:")
        st.write(data_df)

        # Extract RPM and Torque axis, and data values
        # Assuming a specific format where first row is RPM, first column is Torque, and rest is data
        rpm_axis = data_df.columns[1:].astype(float).tolist()
        torque_axis = data_df.iloc[:, 0].astype(float).tolist()
        data = data_df.iloc[:, 1:].values

        st.write(f"RPM Axis: {rpm_axis}")
        st.write(f"Torque Axis: {torque_axis}")

        # Inputs for the new table size and target
        new_torque_target = st.number_input("New torque axis target", value=875, step=25)
        final_table_size = st.text_input("Final table size (rows x cols)", "18x20")

        # Process final table size
        try:
            final_rows, final_cols = map(int, final_table_size.split('x'))
        except ValueError:
            st.error("Invalid table size format. Please enter as 'rows x cols'.")
            st.stop()

        # Ensure data matches axis sizes
        if len(rpm_axis) != data.shape[1] or len(torque_axis) != data.shape[0]:
            st.error("The size of the data does not match the provided RPM or Torque axes.")
            st.stop()

        # Linear regression for each RPM column
        models = {}
        for i, rpm in enumerate(rpm_axis):
            X = np.array(torque_axis).reshape(-1, 1)
            y = data[:, i]
            model = LinearRegression()
            model.fit(X, y)
            models[rpm] = model

        # New torque range for interpolation
        new_torque_range = np.linspace(min(torque_axis), new_torque_target, final_cols)

        # Interpolated data
        interpolated_data = np.zeros((len(new_torque_range), len(rpm_axis)))
        for i, rpm in enumerate(rpm_axis):
            model = models[rpm]
            interpolated_data[:, i] = model.predict(new_torque_range.reshape(-1, 1))

        # Adjust to final size
        final_rpm_range = np.linspace(rpm_axis[0], rpm_axis[-1], final_rows)
        final_data = np.zeros((final_rows, final_cols))

        # Interpolation with checks
        try:
            for i in range(final_cols):
                f = interp1d(rpm_axis, interpolated_data[:, i], kind='linear', bounds_error=False, fill_value="extrapolate")
                final_data[:, i] = f(final_rpm_range)
        except ValueError as e:
            st.error(f"Interpolation error: {e}")
            st.stop()

        # Display and download options
        final_df = pd.DataFrame(final_data, columns=[f'RPM {int(rpm)}' for rpm in final_rpm_range], index=new_torque_range)
        st.write("### Adjusted Table")
        st.dataframe(final_df)

        # Download option
        csv = final_df.to_csv(index_label='Torque')
        st.download_button("Download CSV", csv, "adjusted_table.csv", "text/csv")

    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
