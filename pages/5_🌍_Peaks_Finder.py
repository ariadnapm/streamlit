
from brukeropusreader import read_file
from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import os
import statistics

st.set_page_config(page_title="Peaks Finder", page_icon="🌍", layout="wide")

st.markdown('# Peaks Finder')

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
            minimumx = st.slider("Select minimum value for the x-axis of the plots", np.min(time_array), np.max(time_array), 0.0)
            maximumx = st.slider("Select maximum value for the x-axis of the plots", np.min(time_array), np.max(time_array), np.max(time_array))
            minimumy = st.slider("Select minimum value for the y-axis of the plots", np.min(signal_array), np.max(signal_array), 0.0)
            maximumy = st.slider("Select maximum value for the y-axis of the plots", np.min(signal_array), np.max(signal_array), 0.1)
            range1 = st.slider("Select a first range to look at", min_value=min(min_time), max_value=max(max_time), value=(2.35,2.45))
            range2 = st.slider("Select a second range to look at", min_value=min(min_time), max_value=max(max_time), value=(2.45,2.65))
            range3 = st.slider("Select a third range to look at", min_value=min(min_time), max_value=max(max_time), value=(2.65,2.75))
            minimumy = st.slider("Select minimum value for the y-axis of the plots", np.min(signal_array), np.max(signal_array), 0.0)
            maximumy = st.slider("Select maximum value for the y-axis of the plots", np.min(signal_array), np.max(signal_array), 0.1)
            option = st.selectbox('Legend view', (df.columns[0], df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[5], df.columns[6], df.columns[7], df.columns[8], df.columns[9],  "File Name"))
    

        #Create a line plot RAW DATA
        fig = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram with selected ranges')
        fig.add_vrect(x0=range1[0], x1=range1[1], fillcolor="green", opacity=0.3, layer="below", line_width=0)
        fig.add_vrect(x0=range2[0], x1=range2[1], fillcolor="red", opacity=0.3, layer="below", line_width=0)
        fig.add_vrect(x0=range3[0], x1=range3[1], fillcolor="blue", opacity=0.3, layer="below", line_width=0)
        fig.update_xaxes(range=list([minimumx, maximumx]))
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)



        fig1 = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram Peak 1 (2.35 to 2.45 sec)')
        fig1.update_xaxes(minallowed=2.35, maxallowed=2.45)
        fig1.update_yaxes(range=list([minimumy, maximumy]))
        fig1.update_layout(showlegend=True)
        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)

        fig2 = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram Peak 2 (2.35 to 2.45 sec)')
        fig2.update_xaxes(minallowed=2.45, maxallowed=2.65)
        fig2.update_yaxes(range=list([minimumy, maximumy]))
        fig2.update_layout(showlegend=True)
        st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

        fig3 = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram Peak 3')
        fig3.update_xaxes(minallowed=2.65, maxallowed=2.75)
        fig3.update_yaxes(range=list([minimumy, maximumy]))
        fig3.update_layout(showlegend=True)
        st.plotly_chart(fig3, theme="streamlit", use_container_width=True)

        if st.button("Get Ranges Data"):
            ranges = [range1, range2, range3]
            range_data = []  # Define range_data as an empty list
            for file in uploaded_files:
                for i, r in enumerate(ranges, start=1):
                    filtered_df = combined_df[(combined_df['Time'] >= r[0]) & (combined_df['Time'] <= r[1])]
                    max_point = filtered_df.loc[filtered_df['Signal'].idxmax()]
                    range_info = {
                        'File Name': file.name,
                        'Range': f'Range {i}',
                        'Time of Max Point': max_point['Time'],
                        'Max Point': max_point['Signal']
                    }
                    range_data.append(range_info)

            # Create a dataframe with the range details
            range_df = pd.DataFrame(range_data)
            st.write(range_df)
                    
            # Create a new Excel file containing all combined data
            excelfile = "Chomatogram_selected_ranges_data" + ".xlsx"
            range_df.to_excel(excelfile, index=False)

            # Offer the ranges data file for download
            with open(excelfile, 'rb') as f:
                bytes_data = BytesIO(f.read())
                st.download_button(
                    label="Download Excel Ranges Data File",
                    data=bytes_data,
                    file_name=excelfile,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        peak1 = [2.35, 2.45]
        peak2 = [2.45, 2.65]
        peak3 = [2.65, 2.75]
        
        if st.button("Get Peaks Data"):
            rangespeak = [peak1, peak2, peak3]
            rangepeak_data = []  # Define range_data as an empty list
            for file in uploaded_files:
                for i, r in enumerate(rangespeak, start=1):
                    filtered_df = combined_df[(combined_df['Time'] >= r[0]) & (combined_df['Time'] <= r[1])]
                    max_point = filtered_df.loc[filtered_df['Signal'].idxmax()]
                    rangepeak_info = {
                        'File Name': file.name,
                        'Peak': f'Peak {i}',
                        'Time of Max Point': max_point['Time'],
                        'Max Point': max_point['Signal']
                    }
                    rangepeak_data.append(rangepeak_info)

            # Create a dataframe with the range details
            rangepeak_df = pd.DataFrame(rangepeak_data)
            st.write(rangepeak_df)

            excelfilepeaks = "Chomatogram_peaks_ranges_data" + ".xlsx"
            rangepeak_df.to_excel(excelfilepeaks, index=False)
            
            # Offer the peaks data file for download
            with open(excelfilepeaks, 'rb') as f:
                bytes_data = BytesIO(f.read())
                st.download_button(
                    label="Download Excel Peaks Data File",
                    data=bytes_data,
                    file_name=excelfilepeaks,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
