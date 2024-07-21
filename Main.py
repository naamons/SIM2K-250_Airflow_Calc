import streamlit as st
import pandas as pd

def main():
    st.title("ECU Map Rescaler")

    st.header("Step 1: Input RPM values")
    rpm_input = st.text_area("Enter RPM values (comma separated)", "650,800,992")
    rpm_values = [int(rpm.strip()) for rpm in rpm_input.split(",")]

    st.header("Step 2: Input Original Torque Axis")
    torque_axis_input = st.text_area("Enter original torque axis values (comma separated)", "0,25,50,100,150,200,250,300,350")
    original_torque_axis = [int(torque.strip()) for torque in torque_axis_input.split(",")]

    st.header("Step 3: Input Original Data")
    original_data_input = st.text_area("Enter original data (comma separated rows, with values separated by commas in each row)", 
                                       "111.824,109.492,87.874,93.045,152.942,151.416,144.209,136.452")
    original_data_rows = original_data_input.split("\n")
    original_data = [list(map(float, row.split(","))) for row in original_data_rows]

    st.header("Step 4: Input New Torque Axis")
    new_torque_axis_input = st.text_area("Enter new torque axis values (comma separated)", "30,60,90,120,150")
    new_torque_axis = [int(torque.strip()) for torque in new_torque_axis_input.split(",")]

    if st.button("Generate New Map"):
        # Calculate airflow per torque factor for the given torque axis and airflow values
        airflow_per_torque = [value / original_torque_axis[1] for row in original_data for value in row]

        # Calculate new airflow values using the new torque axis
        new_airflow_values = [[factor * new_torque for new_torque in new_torque_axis] for factor in airflow_per_torque]

        # Create a DataFrame to display the results
        result_df = pd.DataFrame(new_airflow_values, columns=new_torque_axis, index=airflow_per_torque)

        st.write("### New Airflow Values")
        st.dataframe(result_df)

if __name__ == "__main__":
    main()
