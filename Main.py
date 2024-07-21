import streamlit as st
import pandas as pd

def main():
    st.title("ECU Map Rescaler")

    st.header("Step 1: Input RPM values")
    rpm_input = st.text_area("Enter RPM values (one value per line)", "650\n800\n992")
    rpm_values = [int(rpm.strip()) for rpm in rpm_input.split("\n")]

    st.header("Step 2: Input Original Torque Axis")
    torque_axis_input = st.text_area("Enter original torque axis values (one value per line)", "0\n25\n50\n100\n150\n200\n250\n300\n350\n400\n450\n500")
    original_torque_axis = [int(torque.strip()) for torque in torque_axis_input.split("\n")]

    st.header("Step 3: Input Original Data")
    original_data_input = st.text_area("Enter original data (one row per line, values separated by tabs)", 
                                       "0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\n"
                                       "111.824\t109.492\t87.874\t93.045\t88.128\t88.128\t86.22\t82.49\t81.727\t84.228\t84.101\t83.592\t85.161\t84.059\t83.719\t80.625\n"
                                       "174.475\t171.763\t162.394\t167.015\t152.942\t151.416\t144.209\t136.452\t137.893\t141.92\t143.743\t146.837\t144.379\t142.005\t140.733\t127.762")
    original_data_rows = original_data_input.split("\n")
    original_data = [list(map(float, row.split("\t"))) for row in original_data_rows]

    st.header("Step 4: Input New Torque Axis")
    new_torque_axis_input = st.text_area("Enter new torque axis values (one value per line)", "30\n60\n90\n120\n150")
    new_torque_axis = [int(torque.strip()) for torque in new_torque_axis_input.split("\n")]

    if st.button("Generate New Map"):
        # Calculate airflow per torque factor for the given torque axis and airflow values
        airflow_per_torque = [value / torque if torque != 0 else 0 for torque, row in zip(original_torque_axis[1:], original_data[1:]) for value in row]

        # Calculate new airflow values using the new torque axis
        new_airflow_values = [[factor * new_torque for new_torque in new_torque_axis] for factor in airflow_per_torque]

        # Create a DataFrame to display the results
        result_df = pd.DataFrame(new_airflow_values, columns=new_torque_axis, index=[f"Factor {i}" for i in range(len(new_airflow_values))])

        st.write("### New Airflow Values")
        st.dataframe(result_df)

if __name__ == "__main__":
    main()
