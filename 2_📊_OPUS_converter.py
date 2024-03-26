
import streamlit as st
from datetime import datetime
from brukeropusreader import read_file
import pandas as pd
import altair as alt
import numpy as np
import os
import plotly.express as px
import xlsxwriter
from tempfile import NamedTemporaryFile
from io import BytesIO

#################HTML

st.set_page_config(page_title="OPUS File Extractor", page_icon="📊", layout="wide")
st.markdown('# OPUS File Extractor')
st.sidebar.header("OPUS File Extractor")

temp_files_collection = []

# Function to process and extract metadata from OPUS files
def process_opus_files(filelist):
    metadata_list = []
    for file in filelist:
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.getbuffer())
        opus_data = read_file(temp_file.name)
        temp_files_collection.append(temp_file.name)

        # Extract metadata from OPUS file
        optik = opus_data.get("Optik", {})
        AB_data = opus_data.get("AB Data Parameter", {})
        instrument_RF = opus_data.get("Instrument (Rf)", {})
        sample = opus_data.get("Sample", {})
        instrument = opus_data.get("Instrument", {})
        
        # Create a dictionary with metadata
        metadata = {
            "Filename": file.name,
            "Date": AB_data.get("DAT", "n/a"),
            "Time": AB_data.get("TIM", "n/a"),
            "Detector": optik.get("DTC", "n/a"),
            "User": sample.get("CNM", "n/a"),
            "Xpm-file": sample.get("EXP", "n/a"),
            "Sample compartment temperature": str(instrument_RF.get("TSM", "n/a")),
            "Gain": instrument.get("ASG", "n/a"),
            "Ref Gain": instrument.get("ARG", "n/a"),
            "Humidity": instrument.get("HUM", "n/a"),
            "Firmware": instrument.get("VSN", "n/a"),
            "Instrument ID": instrument.get("SRN", "n/a"),
            "Instrument ready?": instrument.get("RDY", "n/a")
        }
        
        metadata_list.append(metadata)
    
    return metadata_list

def delete_files_with_names(directory, file_list):
    for filename in file_list:
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {filename}")


#html settings

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

# Full-width container
container = st.container()
# Create three vertical sections
col1, col2 = container.columns([1,2])
# Section 1: File Upload
with col1:
    # File upload
    uploaded_files = st.file_uploader("Upload OPUS Files", accept_multiple_files=True)




# Section 2: Plots
with col2:
    if uploaded_files:
        metadata_list = process_opus_files(uploaded_files)

        #st.subheader("Data Visualizations")

        combined_df = pd.DataFrame(columns=["Wavenumber (cm^-1)", "Absorbance (AU)", "File"])

        for file in uploaded_files:
            with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.getbuffer())
            opus_data = read_file(temp_file.name)
            temp_files_collection.append(temp_file.name)
        

            ab_x = opus_data.get_range("AB")
            signal = opus_data["AB"][0:len(ab_x)]
            file_df = pd.DataFrame({"Wavenumber (cm^-1)": ab_x[::-1], "Absorbance (AU)": signal[::-1], "File": file.name})
            combined_df = pd.concat([combined_df, file_df])


            ab_x = pd.to_numeric(ab_x, errors='coerce')
            signal = pd.to_numeric(signal, errors='coerce')
            
            min_x = np.min(ab_x)
            max_x = np.max(ab_x)
            min_default = min_x
            max_default = max_x
            
        with col1:
            st.markdown("X-axis of data plot:")
            minimumx = st.slider("Minimum value ", min_x, max_x, min_default)
            maximumx = st.slider("Maximum value ", min_x, max_x, max_default)
                
            with st.expander("Y-axis of data plot:"):
                minimumy = st.slider("Minimum value ", 0.0, 4.0, 0.0)
                maximumy = st.slider("Maximum value ", 0.0, 4.0, 4.0)

        
                #Create a line plot with legend: RAW DATA
        fig = px.line(combined_df, x="Wavenumber (cm^-1)", y="Absorbance (AU)", color = "File", title="Combined Data Line Plot")
        fig.update_xaxes(range=list([minimumx, maximumx]))
        fig.update_yaxes(range=list([minimumy, maximumy]))

        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)







        background_df = pd.DataFrame(columns=["Wavenumber (cm^-1)", "Background Spectra", "File"])

        # Process the uploaded files for background signal graph
        for file in uploaded_files:
            with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.getbuffer())
            opus_data = read_file(temp_file.name)
            temp_files_collection.append(temp_file.name)

            ab_x = opus_data.get_range("AB")
            signal = opus_data["AB"][0:len(ab_x)]
            background_signal = opus_data["ScRf"][0:len(ab_x)]
            background_df = pd.concat([background_df, pd.DataFrame({"Wavenumber (cm^-1)": ab_x[::-1], "Background Spectra": background_signal[::-1], "File": file.name})])


            ab_x = pd.to_numeric(ab_x, errors='coerce')
            background_signal = pd.to_numeric(background_signal, errors='coerce')
            
            min_x = np.min(ab_x)
            max_x = np.max(ab_x)
            min_default = min_x
            max_default = max_x
            
        with col1:
            st.markdown("X-axis of data plot:")
            minimumx = st.slider("Minimum value ", min_x, max_x, min_default)
            maximumx = st.slider("Maximum value ", min_x, max_x, max_default)
                
            with st.expander("Y-axis of background plot:"):
                minimumy = st.slider("Minimum value ", 0.0, 4.0, 0.0)
                maximumy = st.slider("Minimum value ", 0.0, 4.0, 4.0)

        
        fig = px.line(background_df, x="Wavenumber (cm^-1)", y="Background Spectra", color = "File", title="Background Signal Graph")
        fig.update_xaxes(range=list([minimumx, maximumx]))
        fig.update_yaxes(range=list([minimumy, maximumy]))

        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)




# Section 3: Processed files and download buttons
with col1:
  
    if uploaded_files and metadata_list:
        excel_files = {}
        all_data_df = pd.DataFrame()  # Combined DataFrame for all Absorbance and Wavelength data
        wavelength_added = False  # Flag to check if wavelength column is already added

        for index, file in enumerate(uploaded_files):
            with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.getbuffer())
            # Create an Excel file containing the metadata
            opus_data = read_file(temp_file.name)
            temp_files_collection.append(temp_file.name)

            ab_x = opus_data.get_range("AB")
            signal = opus_data["AB"][0:len(ab_x)]

            # Create a DataFrame with "Wavenumber" and "Absorbance" as separate columns
            df = pd.DataFrame({"Wavenumber": ab_x, "Absorbance": signal})


            # Modify the output file name to ensure uniqueness if the names are the same
            new_file_name = file.name.replace('.', '_')  # Replace dot with underscore
            output_file_name = f"{new_file_name}.xlsx"


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
                    key=f"{processed_file}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                )



        for index, file in enumerate(uploaded_files):
            with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.getbuffer())
            opus_data = read_file(temp_file.name)
            temp_files_collection.append(temp_file.name)

            ab_x = opus_data.get_range("AB")
            signal = opus_data["AB"][0:len(ab_x)]
            
            if not wavelength_added:
                wavelength = opus_data.get_range("AB")  # Replace with the actual wavelength data from the OPUS file
                all_data_df["Wavelength"] = wavelength
                wavelength_added = True

            # Create a DataFrame with "Absorbance" data and name the column appropriately
            df = pd.DataFrame({"Absorbance_" + file.name: signal})

            # Add the Absorbance data to the combined DataFrame
            all_data_df = pd.concat([all_data_df, df], axis=1)

            

        # Create a new Excel file containing all combined data
        excelfile_combined = "OPUS_combined_data" + ".xlsx"
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



        # Create an Excel file containing the metadata
        excelfile_metadata = "OPUS_metadata" + ".xlsx"
        workbook_metadata = xlsxwriter.Workbook(excelfile_metadata)
        worksheet_metadata = workbook_metadata.add_worksheet()
        
        # Write the metadata to the Excel file
        headers_metadata = list(metadata_list[0].keys())
        for col, header in enumerate(headers_metadata):
            worksheet_metadata.write(0, col, header)
        
        for row, metadata in enumerate(metadata_list, start=1):
            for col, key in enumerate(metadata):
                worksheet_metadata.write(row, col, str(metadata[key]))
        
        workbook_metadata.close()
        
        
        # Offer the file for download
        with open(excelfile_metadata, 'rb') as f:
            bytes_data = BytesIO(f.read())
            st.download_button(
                label="Download Metadata File",
                data=bytes_data,
                file_name=excelfile_metadata,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )




# delete temp files in cache and memory

directory_path = ""
files_to_delete = temp_files_collection

delete_files_with_names(directory_path, temp_files_collection)
    
