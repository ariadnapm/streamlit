from tempfile import NamedTemporaryFile
from brukeropusreader import read_file
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO, StringIO
import statistics
import os


st.set_page_config(page_title="Chromatogram Graph Tool", page_icon="🌍", layout="wide")

##############################################html settings
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

################# Section 1: File Upload

with col1:
    uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)
    
def Average(lst): 
    return sum(lst) / len(lst) 




with col2:
    if uploaded_files:
        combined_df = pd.DataFrame()
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
            signal_array = data["Signal"]
            


            tid_array = pd.to_numeric(tid_array, errors='coerce')
            signal_array = pd.to_numeric(signal_array, errors='coerce')

            min_x = np.min(tid_array)
            min_default = 5.0
            max_x = np.max(tid_array)
            max_default = 40.0


            file_df = pd.DataFrame({"Time": tid_array, "Signal": signal_array, df.columns[0]: SampleName, df.columns[1]: LV_SampleInfo, df.columns[2]: SampleSetId, df.columns[3]: LV_Batch, df.columns[4]: SampleSetName, df.columns[5]: SampleSetStartDate, df.columns[6]: InjectionVolume, df.columns[7]: SystemName, df.columns[8]: LV_BatchID, df.columns[9]: SampleType, "File Name": filename})
            combined_df = pd.concat([combined_df, file_df], ignore_index=True)

            #find maximum signal point
            max_signal = np.max(signal_array)
            max_signals_points.append(max_signal)

            #find index of the max signal point
            index = pd.Index(signal_array).get_loc(max_signal)
            
            #using the index, find the time of the max signal point
            max_signal_time = tid_array[index]
            max_signals_time.append(max_signal_time)
        
        with col1:
            minimumx = st.slider("Select minimum value for the x-axis of the plot", min_x, max_x, min_default)
            maximumx = st.slider("Select maximum value for the x-axis of the plot", min_x, max_x, max_default)
            option = st.selectbox('Legend view', (df.columns[0], df.columns[1], df.columns[2], df.columns[3], df.columns[4], df.columns[5], df.columns[6], df.columns[7], df.columns[8], df.columns[9],  "File Name"))
            with st.expander("Y-axis:"):
                minimumy = st.slider("Select minimum value for the y-axis of the plot", -1.0, 1.0, -0.1)
                maximumy = st.slider("Select maximum value for the y-axis of the plot", -1.0, 1.0, 0.1)

        #Create a line plot with legend: RAW DATA
        fig = px.line(combined_df, x="Time", y="Signal", color = option, title='Chomatogram')
        fig.update_xaxes(range=list([minimumx, maximumx]))
        fig.update_yaxes(range=list([minimumy, maximumy]))

        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)



        average_time = Average(max_signals_time)  
        average_time = pd.to_numeric(average_time, errors='coerce')

        #Create a line plot with legend: X-SHIFTED GRAPH
        max_signal_of_all = np.max(max_signals_points)  
        max_signal_of_all = pd.to_numeric(max_signal_of_all, errors='coerce')
    
        combined_x_shifted_df = pd.DataFrame()  # Initialize an empty DataFrame to store shifted data

        for file, max_signal, signal_array in zip(uploaded_files, max_signals_points, max_signals_time):
            file_contents = file.getvalue().decode()
            filename = file.name
            df = pd.read_csv(StringIO(file_contents), delimiter='\t')
            #collect info data from the file
            df_info = df.loc[0]        

            
            #collect time and signal data from the file and add it to the combined_df
            data = df.loc[1:]
            data = data.iloc[:, 0:2]
            data = data.rename(columns={df.columns[0]: 'Time', df.columns[1]: 'Signal'})
                
            tid_array = data["Time"]
            signal_array = data["Signal"]
            SampleName = df_info.iloc[0]

            tid_array = pd.to_numeric(tid_array, errors='coerce')
            signal_array = pd.to_numeric(signal_array, errors='coerce')

            #find maximum signal point
            max_signal = np.max(signal_array)
            max_signals_points.append(max_signal)
            
            #using the index, find the time of the max signal p

            if max_signal < max_signal_of_all:
                difference = max_signal_of_all / max_signal
                x_signal_array = signal_array * difference

            else:
                x_signal_array = signal_array


            x_shifted_df = pd.DataFrame({"Time": tid_array, "Signal": x_signal_array,  df.columns[0]: SampleName, df.columns[1]: LV_SampleInfo, df.columns[2]: SampleSetId, df.columns[3]: LV_Batch, df.columns[4]: SampleSetName, df.columns[5]: SampleSetStartDate, df.columns[6]: InjectionVolume, df.columns[7]: SystemName, df.columns[8]: LV_BatchID, df.columns[9]: SampleType, "File Name": filename})

            combined_x_shifted_df  = pd.concat([combined_x_shifted_df , x_shifted_df],  ignore_index=True)
        

        #Create a line plot with legend: Y-SHIFTED
        fig_x_shifted  = px.line(combined_x_shifted_df , x="Time", y="Signal", color = option, title='Chomatogram y-shifted')
        fig_x_shifted.update_layout(showlegend=True)
        fig_x_shifted.update_xaxes(range=list([minimumx, maximumx]))
        fig_x_shifted.update_yaxes(range=list([minimumy, maximumy]))

        st.plotly_chart(fig_x_shifted , theme="streamlit", use_container_width=True)
    

        combined_xy_shifted_df = pd.DataFrame()  # Initialize an empty DataFrame to store shifted data            

        #Create a line plot with legend: XY-SHIFTED GRAPH

        for file, max_signal, max_signal_time in zip(uploaded_files, max_signals_points, max_signals_time):
            file_contents = file.getvalue().decode()
    
            df = pd.read_csv(StringIO(file_contents), delimiter='\t')
            #collect info data from the file
            df_info = df.loc[0]        
            filename = file.name
            
            #collect time and signal data from the file and add it to the combined_df
            data = df.loc[1:]
            data = data.iloc[:, 0:2]
            data = data.rename(columns={df.columns[0]: 'Time', df.columns[1]: 'Signal'})
                
            tid_array = data["Time"]
            signal_array = data["Signal"]
            SampleName = df_info.iloc[0]


            tid_array = pd.to_numeric(tid_array, errors='coerce')
            signal_array = pd.to_numeric(signal_array, errors='coerce')


            #find maximum signal point
            max_signal = np.max(signal_array)
            max_signals_points.append(max_signal)


            #find index of the max signal point (time)
            index = pd.Index(signal_array).get_loc(max_signal)
            time_at_index = tid_array[index]
            
            #using the index, find the time of the max signal point
            
            #shift time
            if time_at_index < average_time:
                difference_t = average_time / time_at_index
                xy_signal_time_array = tid_array * difference_t

            else:
                difference_t = time_at_index / average_time 
                xy_signal_time_array = tid_array / difference_t


            #normalised signals
            if max_signal < max_signal_of_all:
                difference = max_signal_of_all / max_signal
                xy_signal_array = signal_array * difference

            else:
                xy_signal_array = signal_array


            xy_shifted_df = pd.DataFrame({"Time": xy_signal_time_array, "Signal": xy_signal_array,  df.columns[0]: SampleName, df.columns[1]: LV_SampleInfo, df.columns[2]: SampleSetId, df.columns[3]: LV_Batch, df.columns[4]: SampleSetName, df.columns[5]: SampleSetStartDate, df.columns[6]: InjectionVolume, df.columns[7]: SystemName, df.columns[8]: LV_BatchID, df.columns[9]: SampleType, "File Name": filename})
            combined_xy_shifted_df  = pd.concat([combined_xy_shifted_df , xy_shifted_df],  ignore_index=True)

        #Create a line plot with legend: XY-SHIFTED
        fig_xy_shifted  = px.line(combined_xy_shifted_df , x="Time", y="Signal", color = option, title='Chomatogram xy-shifted')
        fig_xy_shifted.update_layout(showlegend=True)
        fig_xy_shifted.update_xaxes(range=list([minimumx, maximumx]))
        fig_xy_shifted.update_yaxes(range=list([minimumy, maximumy]))

        st.plotly_chart(fig_xy_shifted , theme="streamlit", use_container_width=True)
        



with col1:
  
    if uploaded_files:
        excel_files = {}
        all_data_df = pd.DataFrame()  # Combined DataFrame for all Absorbance and Wavelength data
        combined_df = pd.DataFrame()
        time_added = False
        for index, file in enumerate(uploaded_files):
            with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.getbuffer())
            # Create an Excel file containing the metadata
            chroma_data = read_file(temp_file.name)
            temp_files_collection.append(temp_file.name)
            
            file_contents = file.getvalue().decode()
            df = pd.read_csv(StringIO(file_contents), delimiter='\t')


            data = df.loc[1:]
            data = data.iloc[:, 0:2]
            data = data.rename(columns={df.columns[0]: 'Time', df.columns[1]: 'Signal'})
                
            tid_array = data["Time"]
            signal_array = data["Signal"]
            tid_array = pd.to_numeric(tid_array, errors='coerce')
            signal_array = pd.to_numeric(signal_array, errors='coerce')
            

            # Modify the output file name to ensure uniqueness if the names are the same
            new_file_name = file.name.replace('.', '_')  # Replace dot with underscore
            output_file_name = f"{new_file_name}.xlsx"


            #read file and forget first two lines - (info_lines)
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

    
          
            df = pd.DataFrame({"Time": tid_array, "Signal": signal_array, df.columns[0]: SampleName, df.columns[1]: LV_SampleInfo, df.columns[2]: SampleSetId, df.columns[3]: LV_Batch, df.columns[4]: SampleSetName, df.columns[5]: SampleSetStartDate, df.columns[6]: InjectionVolume, df.columns[7]: SystemName, df.columns[8]: LV_BatchID, df.columns[9]: SampleType, "File Name": filename})
            combined_df = pd.concat([combined_df, file_df], ignore_index=True)

            # Write the DataFrame to an Excel file
            df.to_excel(output_file_name, index=False)
            excel_files[file.name] = output_file_name

        
            # Provide a download link to the processed Excel file
        for input_file, processed_file in excel_files.items():
            with open(processed_file, 'rb') as f:
                bytes_data = BytesIO(f.read())
                st.download_button(
                    label=f"Download Processed File {processed_file}",
                    data=bytes_data,
                    file_name=output_file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"{processed_file}"
                )



        for index, file in enumerate(uploaded_files):
            with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.getbuffer())
            opus_data = read_file(temp_file.name)
            temp_files_collection.append(temp_file.name)

            file_contents = file.getvalue().decode()
            df = pd.read_csv(StringIO(file_contents), delimiter='\t')


            data = df.loc[1:]
            data = data.iloc[:, 0:2]
            data = data.rename(columns={df.columns[0]: 'Time', df.columns[1]: 'Signal'})
                
            tid_array = data["Time"]
            signal_array = data["Signal"]
            tid_array = pd.to_numeric(tid_array, errors='coerce')
            signal_array = pd.to_numeric(signal_array, errors='coerce')
            

            
            if not time_added:
                time_added = tid_array  # Replace with the actual wavelength data from the OPUS file
                all_data_df["Signal"] = signal_array
                time_added = True

            # Create a DataFrame with "Absorbance" data and name the column appropriately
            df = pd.DataFrame({"Signal_" + file.name: signal_array})

            # Add the Absorbance data to the combined DataFrame
            all_data_df = pd.concat(["Time": tid_array, df], axis=1)

            

        # Create a new Excel file containing all combined data
        excelfile_combined = "Chromatogram_combined_data" + ".xlsx"
        all_data_df.to_excel(excelfile_combined, index=False)

        # Offer the combined data file for download
        with open(excelfile_combined, 'rb') as f:
            bytes_data = BytesIO(f.read())
            st.download_button(
                label="Download Combined Data File",
                data=bytes_data,
                file_name=excelfile_combined,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
