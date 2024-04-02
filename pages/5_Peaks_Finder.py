
from brukeropusreader import read_file
from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import os
import statistics

st.set_page_config(page_title="Chromatogram Graph Tool", page_icon="🌍", layout="wide")

st.markdown('# Chromatogram Graph Tool')
st.sidebar.header("Chromatogram Graph Tool")

st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

container = st.container()
col1, col2 = container.columns([1,2])

temp_files_collection = []


# Function to process each file and return the maximum point within the specified range
def process_file(file, range_start, range_end):
    df = pd.read_csv(file)
    filtered_df = df[(df['Time'] >= range_start) & (df['Time'] <= range_end)]
    max_point = filtered_df.loc[filtered_df['Signal'].idxmax()]
    return max_point

with col1:
    uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)
    
with col2:
    if uploaded_files:
        combined_df = pd.DataFrame()
        min_time = []
        max_time = []
        
        max_signals_points = []
        max_signals_time = []

        for file in uploaded_files:

            #read file and forget first two lines - (info_lines)
            df = pd.read_table(file)
            filename = file.name
            
            #collect info data from the file
            df_info = df.loc[0]      
            SampleName =  df_info.iloc[0]
            LV_SampleInfo =  df_info.iloc[1]
            SampleSetId =  df_info.iloc[2]
            LV_Batch =  df_info.iloc[3]
            SampleSetName =  df_info.iloc[4]
            SampleSetStartDate =  df_info.iloc[5]
            InjectionVolume =  df_info.iloc[6]
            SystemName =  df_info.iloc[7]
            LV_BatchID =  df_info.iloc[8]
            SampleType =  df_info.iloc[9]

            
            #collect time and signal data from the file and add it to the combined_df
            data = df.loc[1:]
            data = data.iloc[:, 0:2]
            data = data.rename(columns={df.columns[0]: 'Time', df.columns[1]: 'Signal'})
                
            tid_array = data["Time"]
            tid_array = pd.to_numeric(tid_array, errors='coerce')
            signal_array = data["Signal"]
            signal_array = pd.to_numeric(signal_array, errors='coerce')

            file_df = pd.DataFrame({"Time": tid_array, "Signal": signal_array, df.columns[0]: SampleName, df.columns[1]: LV_SampleInfo, df.columns[2]: SampleSetId, df.columns[3]: LV_Batch, df.columns[4]: SampleSetName, df.columns[5]: SampleSetStartDate, df.columns[6]: InjectionVolume, df.columns[7]: SystemName, df.columns[8]: LV_BatchID, df.columns[9]: SampleType, "File Name": filename})
            combined_df = pd.concat([combined_df, file_df], ignore_index=True)

            min_x = np.min(tid_array)
            min_time.append(min_x)
            
            max_x = np.max(tid_array)
            max_time.append(max_x)

            #find maximum signal point
            max_signal = np.max(signal_array)
            max_signals_points.append(max_signal)

            #find index of the max signal point
            index = pd.Index(signal_array).get_loc(max_signal)
            
            #using the index, find the time of the max signal point
            max_signal_time = tid_array[index]
            max_signals_time.append(max_signal_time)
        
        with col1:
            range1 = st.slider("Select a first range to look at", min_value=min(min_time), max_value=max(max_time), value=(0.0,10.0))
            range2 = st.slider("Select a second range to look at", min_value=min(min_time), max_value=max(max_time), value=(10.0,20.0))
            range3 = st.slider("Select a third range to look at", min_value=min(min_time), max_value=max(max_time), value=(20.0,25.0))

            option = st.selectbox('Legend view', (df.columns[0], df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[5], df.columns[6], df.columns[7], df.columns[8], df.columns[9],  "File Name"))
    

        #Create a line plot with legend: RAW DATA
        fig = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram')
        fig.add_vrect(x0=range1[0], x1=range1[1], fillcolor="green", opacity=0.3, layer="below", line_width=0)
        fig.add_vrect(x0=range2[0], x1=range2[1], fillcolor="red", opacity=0.3, layer="below", line_width=0)
        fig.add_vrect(x0=range3[0], x1=range3[1], fillcolor="blue", opacity=0.3, layer="below", line_width=0)
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)


        if st.button("Get Data"):
            ranges = [range1, range2, range3]
            range_data = []  # Define range_data as an empty list
            for file in uploaded_files:
                for i, r in enumerate(ranges, start=1):
                    filtered_df = combined_df[(combined_df['Time'] >= r[0]) & (combined_df['Time'] <= r[1])]
                    min_value = filtered_df['Signal'].min()
                    max_value = filtered_df['Signal'].max()
                    max_point = filtered_df.loc[filtered_df['Signal'].idxmax()]
                    range_info = {
                        'File Name': file.name,
                        'Range': f'Range {i}',
                        'Min Value': min_value,
                        'Max Value': max_value,
                        'Time of Max Point': max_point['Time'],
                        'Max Point': max_point['Signal']
                    }
                    range_data.append(range_info)

            # Create a dataframe with the range details
            range_df = pd.DataFrame(range_data)
            st.write(range_df)



                        # Create a new Excel file containing all combined data
            excelfile = "OPUS_combined_data" + ".xlsx"
            range_df.to_excel(excelfile, index=False)

            # Offer the combined data file for download
            with open(excelfile, 'rb') as f:
                bytes_data = BytesIO(f.read())
                st.download_button(
                    label="Download Excel Data File",
                    data=bytes_data,
                    file_name=excelfile,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
