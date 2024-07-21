import streamlit as st
import pandas as pd

def main():
    st.title("ECU Map Rescaler")

    st.header("Step 1: Paste the entire map with both axes and data")
    map_input = st.text_area("Paste the map (including both axes and data, tab-separated)", 
                             "650\t800\t992\t1248\t1500\t1750\t2016\t2496\t3008\t3488\t4000\t4512\t4992\t5504\t6016\t6592\n"
                             "0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\n"
                             "25\t111.824\t109.492\t87.874\t93.045\t88.128\t88.128\t86.22\t82.49\t81.727\t84.228\t84.101\t83.592\t85.161\t84.059\t83.719\t80.625\n"
                             "50\t174.475\t171.763\t162.394\t167.015\t152.942\t151.416\t144.209\t136.452\t137.893\t141.92\t143.743\t146.837\t144.379\t142.005\t140.733\t127.762")
    
    st.header("Step 2: Input New Torque Axis")
    new_torque_axis_input = st.text_area("Enter new torque axis values (one value per line)", "30\n60\n90\n120\n150")
    new_torque_axis = [int(torque.strip()) for torque in new_torque_axis_input.split("\n")]

    if st.button("Generate New Map"):
        # Split the input into lines
        map_lines = map_input.split("\n")
        
        # Extract RPM values from the first line
        rpm_values = [int(rpm) for rpm in map_lines[0].split("\t")[1:]]

        # Extract original torque axis and data
        original_torque_axis = []
        original_data = []
        for line in map_lines[1:]:
            parts = line.split("\t")
            original_torque_axis.append(int(parts[0]))
            original_data.append(list(map(float, parts[1:])))

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
