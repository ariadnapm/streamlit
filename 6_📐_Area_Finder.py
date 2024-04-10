from brukeropusreader import read_file
from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import os
import statistics

st.set_page_config(page_title="Area Finder", page_icon="📐", layout="wide")

st.markdown('# Area Finder')

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Preselected ranges", "Peak 1", "Peak 2", "Peak 3", "Peak Area% Scatter Plot"])

range_data = []
rangepeak_data = []
rangepeakper_data = []

with st.container():  
    uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)

    if uploaded_files:
        combined_df = pd.DataFrame()
        min_time = []
        max_time = []
        
        max_signals_points = []
        max_signals_time = []
        
        ranges = [[2.35,2.45], [2.45,2.65], [2.65,2.75]]
        rangespeak = [[2.35, 2.45], [2.45, 2.65], [2.65, 2.75]]
        rangespeakper = [[2.35, 2.45], [2.45, 2.65], [2.65, 2.75]]

    
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

            #find index of the max signal pointbatch
            index = pd.Index(signal_array).get_loc(max_signal)
            
            #using the index, find the time of the max signal point
            max_signal_time = tid_array[index]
            max_signals_time.append(max_signal_time)
            
            file_ranges_data = []

            for i, r in enumerate(ranges, start=1):
                filtered_df2 = combined_df[(combined_df['Time'] >= r[0])]
                filtered_df2 = filtered_df2[(filtered_df2['Time'] <= r[1])]
                
                area2 = np.trapz(filtered_df2['Signal'], filtered_df2['Time'])  # Calculate the area using the trapezoidal rule
                
                max_point2 = filtered_df2.loc[filtered_df2['Signal'].idxmax()]
                
                range_info = {
                    'File Name': file.name,
                    'Range': f'Range {i}',
                    'Time of Max Point': max_point2['Time'],
                    'Max Point': max_point2['Signal'],
                    'Area': area2
                }
                file_ranges_data.append(range_info)
            range_data.extend(file_ranges_data)
            
            file_peak_data = []

            for i, r in enumerate(rangespeak, start=1):
                filtered_df1 = combined_df[(combined_df['Time'] >= r[0])]
                filtered_df1 = filtered_df1[(filtered_df1['Time'] <= r[1])]

                area1 = np.trapz(filtered_df1['Signal'], filtered_df1['Time'])
                
                max_point1 = filtered_df1.loc[filtered_df1['Signal'].idxmax()]
                                
                rangepeak_info = {
                    'File Name': file.name,
                    'Peak': f'Peak {i}',
                    'Time of Max Point': max_point1['Time'],
                    'Max Point': max_point1['Signal'],
                    'Area': area1,
                    df.columns[0]: SampleName
                }
                
                file_peak_data.append(rangepeak_info)
            rangepeak_data.extend(file_peak_data)
            
            file_peakper_data = []

            for i, r in enumerate(rangespeakper, start=1):

                filtered_df = combined_df[(combined_df['Time'] >= r[0]) & (combined_df['Time'] <= r[1])]
                max_point = filtered_df.loc[filtered_df['Signal'].idxmax()]

                areaper = np.trapz(filtered_df['Signal'], filtered_df['Time'])  # Calculate the area using the trapezoidal rule
                                
                staticfiltered_df = combined_df[(combined_df['Time'] >= 10.0) & (combined_df['Time'] <= 15.0)]
                staticmax_point = staticfiltered_df.loc[staticfiltered_df['Signal'].idxmax()]
                staticarea = np.trapz(staticfiltered_df['Signal'], staticfiltered_df['Time'])  # Calculate the area using the trapezoidal rule

                tid_array = np.array(tid_array)
                sample_rate = (tid_array[1] - tid_array[0])*60

                rangepeakper_info = {
                            'File Name': file.name,
                            'Peak': f'Peak {i}',
                            'Time of Max Point': max_point['Time'],
                            'Max Point%': max_point['Signal']/staticmax_point['Signal']*100,
                            'Max Point Area%': areaper/staticarea*100 ,
                            'Area per sample rate': areaper/sample_rate*(1000000),
                            df.columns[0]: SampleName,
                            df.columns[1]: LV_SampleInfo, 
                            df.columns[2]: SampleSetId, 
                            df.columns[3]: LV_Batch, 
                            df.columns[4]: SampleSetName, 
                            df.columns[5]: SampleSetStartDate, 
                            df.columns[6]: InjectionVolume, 
                            df.columns[7]: SystemName, 
                            df.columns[8]: LV_BatchID, 
                            df.columns[9]: SampleType
                }
                file_peakper_data.append(rangepeakper_info)
            rangepeakper_data.extend(file_peakper_data)

        if st.button("Get Ranges Data"):
        
            range_df = pd.DataFrame(range_data)
            st.write(range_df)
                              
            excelfile = "Chomatogram_selected_ranges_data" + ".xlsx"
            range_df.to_excel(excelfile, index=False)

            with open(excelfile, 'rb') as f:
                bytes_data = BytesIO(f.read())
                st.download_button(
                    label="Download Excel Ranges Data File",
                    data=bytes_data,
                    file_name=excelfile,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        if st.button("Get Peaks Data"):
                      
            rangepeak_df = pd.DataFrame(rangepeak_data)
            st.write(rangepeak_df)

            excelfilepeaks = "Chomatogram_peaks_ranges_data" + ".xlsx"
            rangepeak_df.to_excel(excelfilepeaks, index=False)
                        
            with open(excelfilepeaks, 'rb') as f:
                bytes_data = BytesIO(f.read())
                st.download_button(
                    label="Download Excel Peaks Data File",
                    data=bytes_data,
                    file_name=excelfilepeaks,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        if st.button("Get Peaks% Data"):
   
            rangepeakper_df = pd.DataFrame(rangepeakper_data)
            st.write(rangepeakper_df)         
            
            option1 = st.selectbox('X-axis view for Pear Area% Plot', (df.columns[0], df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[5], df.columns[6], df.columns[7], df.columns[8], df.columns[9],  "File Name"))

            scatter_fig = px.scatter(rangepeakper_df, x=option1, y='Max Point Area%', text='Max Point Area%', 
                                        title='Peak Area Percentage by Sample', color='Peak', 
                                        labels={'File Name': 'Sample',
                                                'Max Point Area%': 'Peak Area %',
                                                df.columns[0]: SampleName,
                                                df.columns[1]: LV_SampleInfo,
                                                df.columns[2]: SampleSetId,
                                                df.columns[3]: LV_Batch,
                                                df.columns[4]: SampleSetName,
                                                df.columns[5]: SampleSetStartDate,
                                                df.columns[6]: InjectionVolume,
                                                df.columns[7]: SystemName,
                                                df.columns[8]: LV_BatchID,
                                                df.columns[9]: SampleType}, 
                                        color_discrete_sequence=px.colors.qualitative.Set1)
            
            scatter_fig.update_layout(xaxis={'categoryorder': 'category ascending'}, xaxis_title='Sample', yaxis_title='Peak Area %')
            scatter_fig.update_traces(showlegend=True, mode='markers+lines')                       
            
            excelfilepeaksper = "Chomatogram_peaks%_ranges_data" + ".xlsx"
            rangepeakper_df.to_excel(excelfilepeaksper, index=False)
                       
                        # Offer the peaks data file for download
            with open(excelfilepeaksper, 'rb') as f:
                bytes_data = BytesIO(f.read())
                st.download_button(
                    label="Download Excel Peaks% Data File",
                    data=bytes_data,
                    file_name=excelfilepeaksper,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            with tab5:
                st.plotly_chart(scatter_fig, use_container_width=True)
        
        
        minimumx = st.slider("Select minimum value for the x-axis of the plots",  min_value=min(min_time), max_value=max(max_time), value=min(min_time), key= "minx")
        maximumx = st.slider("Select maximum value for the x-axis of the plots",  min_value=min(min_time), max_value=max(max_time), value=max(max_time), key= "maxx")
        range1 = st.slider("Select a first range to look at", min_value=min(min_time), max_value=max(max_time), value=(2.35,2.45), key= "r1")
        range2 = st.slider("Select a second range to look at", min_value=min(min_time), max_value=max(max_time), value=(2.45,2.65), key= "r2")
        range3 = st.slider("Select a third range to look at", min_value=min(min_time), max_value=max(max_time), value=(2.65,2.75), key= "r3")
        minimumy = st.slider("Select minimum value for the y-axis of the plots", min_value=np.min(signal_array), max_value=np.max(signal_array), value=0.0, key= "miny")
        maximumy = st.slider("Select maximum value for the y-axis of the plots", min_value=np.min(signal_array), max_value=np.max(signal_array), value=0.1, key= "maxy")
        option = st.selectbox('Legend view', (df.columns[0], df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[5], df.columns[6], df.columns[7], df.columns[8], df.columns[9],  "File Name"))
        


        with tab1:
                fig = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram with selected ranges')
                fig.add_vrect(x0=range1[0], x1=range1[1], fillcolor="green", opacity=0.3, layer="below", line_width=0)
                fig.add_vrect(x0=range2[0], x1=range2[1], fillcolor="red", opacity=0.3, layer="below", line_width=0)
                fig.add_vrect(x0=range3[0], x1=range3[1], fillcolor="blue", opacity=0.3, layer="below", line_width=0)
                fig.add_vrect(x0=10.0, x1=15.0, fillcolor="yellow", opacity=0.3, layer="below", line_width=0)
                fig.update_xaxes(range=list([minimumx, maximumx]))
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with tab2:
                fig1 = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram Peak 1 (2.35 to 2.45 sec)')
                fig1.update_xaxes(minallowed=2.35, maxallowed=2.45)
                fig1.update_yaxes(range=list([minimumy, maximumy]))
                fig1.update_layout(showlegend=True)
                st.plotly_chart(fig1, theme="streamlit", use_container_width=True)

        with tab3:
                fig2 = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram Peak 2 (2.35 to 2.45 sec)')
                fig2.update_xaxes(minallowed=2.45, maxallowed=2.65)
                fig2.update_yaxes(range=list([minimumy, maximumy]))
                fig2.update_layout(showlegend=True)
                st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

        with tab4:
                fig3 = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram Peak 3')
                fig3.update_xaxes(minallowed=2.65, maxallowed=2.75)
                fig3.update_yaxes(range=list([minimumy, maximumy]))
                fig3.update_layout(showlegend=True)
                st.plotly_chart(fig3, theme="streamlit", use_container_width=True)
                       

