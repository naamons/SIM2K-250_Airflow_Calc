import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Streamlit app
st.title("3D Table Adjuster")
st.write("Upload your Excel file with the table data.")

# File upload
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Read the Excel file
    try:
        df = pd.read_excel(uploaded_file, sheet_name=None)  # Reading all sheets

        # Display available sheets and select the first sheet
        sheet_names = list(df.keys())
        st.write("Sheets found:", sheet_names)
        first_sheet_name = sheet_names[0]
        data_df = df[first_sheet_name]

        # Display the data
        st.write("Data from the first sheet:")
        st.write(data_df)

        # Extract RPM and Torque axis, and data values
        rpm_axis = data_df.columns[1:].astype(float).tolist()
        torque_axis = data_df.iloc[:, 0].astype(float).tolist()
        data = data_df.iloc[:, 1:].values

        st.write(f"RPM Axis: {rpm_axis}")
        st.write(f"Torque Axis: {torque_axis}")

        # Inputs for the new torque target
        new_torque_target = st.number_input("New torque axis target", value=875, step=25)

        # Determine the number of rows and columns to maintain the original size
        original_rows = len(torque_axis)
        original_cols = len(rpm_axis)

        # Create a new torque axis with the same number of points, extending to the new maximum
        new_torque_range = np.linspace(min(torque_axis), new_torque_target, original_rows)

        # Linear regression for each RPM column
        models = {}
        for i, rpm in enumerate(rpm_axis):
            X = np.array(torque_axis).reshape(-1, 1)
            y = data[:, i]
            model = LinearRegression()
            model.fit(X, y)
            models[rpm] = model

        # Interpolate the data to the new torque range
        new_data = np.zeros((original_rows, original_cols))
        for i, rpm in enumerate(rpm_axis):
            model = models[rpm]
            new_data[:, i] = model.predict(new_torque_range.reshape(-1, 1))

        # Adjust data scaling to align with original values
        original_max_torque = max(torque_axis)
        scaling_factor = original_max_torque / new_torque_target
        new_data = new_data * scaling_factor

        # Display and download options
        final_df = pd.DataFrame(new_data, columns=[f'RPM {int(rpm)}' for rpm in rpm_axis], index=new_torque_range)
        final_df.index.name = 'Torque'
        st.write("### Adjusted Table")
        st.dataframe(final_df)

        # Download option
        csv = final_df.to_csv(index=True)
        st.download_button("Download CSV", csv, "adjusted_table.csv", "text/csv")

    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
