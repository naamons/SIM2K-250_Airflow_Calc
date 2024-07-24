import streamlit as st
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d

# Streamlit app
st.title("3D Table Adjuster")
st.write("Paste your table data, set axes, and define the new torque axis and table size.")

# Inputs
rpm_axis = st.text_area("RPM axis", "550\t650\t800\t1000\t1300\t1500\t1750\t2000\t2500\t3000\t3500\t4000\t4500\t5000\t5200\t5500\t6000\t6600")
torque_axis = st.text_area("Torque axis", "20\n40\n60\n80\n100\n125\n150\n175\n200\n250\n300\n350\n400\n450\n500\n550\n600\n650\n700\n750")
data = st.text_area("Data", "50.02\t50.02\t50.02\t50.02\t51.97\t50.02\t55.7\t50.359\t50.02\t50.698\t55.276\t54.979\t54.471\t60.405\t55.997\t56.76\t58.71\t55.785\n..."
                   "\n... (more data rows)")
new_torque_target = st.number_input("New torque axis target", value=875, step=25)
final_table_size = st.text_input("Final table size (rows x cols)", "18x20")

# Parse the input
try:
    rpm_axis = list(map(float, rpm_axis.split('\t')))
    torque_axis = list(map(float, torque_axis.split('\n')))
    data = np.array([list(map(float, row.split('\t'))) for row in data.split('\n') if row])
    final_rows, final_cols = map(int, final_table_size.split('x'))
except ValueError:
    st.error("Please ensure all inputs are in the correct format.")
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
for i in range(final_cols):
    f = interp1d(rpm_axis, interpolated_data[:, i], kind='linear')
    final_data[:, i] = f(final_rpm_range)

# Display and download options
final_df = pd.DataFrame(final_data, columns=[f'RPM {int(rpm)}' for rpm in final_rpm_range], index=new_torque_range)
st.write("### Adjusted Table")
st.dataframe(final_df)

# Download option
csv = final_df.to_csv(index_label='Torque')
st.download_button("Download CSV", csv, "adjusted_table.csv", "text/csv")
