import streamlit as st
from datetime import datetime
from brukeropusreader import read_file
import pandas as pd
import altair as alt
import os
import xlsxwriter
from tempfile import NamedTemporaryFile
from io import BytesIO

#################HTML

st.set_page_config(layout="wide", page_title="OPUS File Extractor", page_icon="📊")
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
        optik = opus_data["Optik"]
        AB_data = opus_data["AB Data Parameter"]
        instrument_RF = opus_data["Instrument (Rf)"]
        sample = opus_data["Sample"]
        instrument = opus_data["Instrument"]
        
        # Create a dictionary with metadata
        metadata = {
            "Filename": file.name,
            "Date": AB_data["DAT"],
            "Time": AB_data["TIM"],
            "Detector": optik["DTC"],
            "User": sample["CNM"],
            "Xpm-file": sample["EXP"],
            "Sample compartment temperature": str(instrument_RF["TSM"]),
            "Gain": instrument["ASG"],
            "Ref Gain": instrument["ARG"],
            "Humidity": instrument["HUM"],
            "Firmware": instrument["VSN"],
            "Instrument ID": instrument["SRN"],
            "Instrument ready?": instrument["RDY"]
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
col1, col2, col3 = container.columns(3)
# Section 1: File Upload
with col1:
    # File upload
    uploaded_files = st.file_uploader("Upload OPUS Files", accept_multiple_files=True)




# Section 2: Plots
with col2:
    if uploaded_files:
        metadata_list = process_opus_files(uploaded_files)

        st.subheader("Data Visualizations")

        combined_df = pd.DataFrame(columns=["Wavenumber (cm^-1)", "Absorbance (AU)", "File"])

        for file in uploaded_files:
            with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.getbuffer())
            opus_data = read_file(temp_file.name)
            temp_files_collection.append(temp_file.name)
        

            ab_x = opus_data.get_range("AB")
            signal = opus_data["AB"][0:len(ab_x)]
            file_df = pd.DataFrame({"Wavenumber (cm^-1)": ab_x, "Absorbance (AU)": signal, "File": file.name})
            combined_df = pd.concat([combined_df, file_df])

        # Create a line plot for the combined data with legend
        line_plot = alt.Chart(combined_df).mark_line().encode(
            x=alt.X('Wavenumber (cm^-1):Q', title='Wavenumber (cm^-1)', scale=alt.Scale(reverse=True)),
            y=alt.Y('Absorbance (AU):Q', title='Absorbance (AU)'),
            color='File:N'
        ).properties(
            width=600,
            height=400
        )
        # Display the line plot
        st.subheader("Combined Data Line Plot")
        st.altair_chart(line_plot, use_container_width=True)





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
            background_df = pd.concat([background_df, pd.DataFrame({"Wavenumber (cm^-1)": ab_x, "Background Spectra": background_signal, "File": file.name})])


        # Create a line plot for the background spectra
        background_line_plot = alt.Chart(background_df).mark_line().encode(
            x=alt.X('Wavenumber (cm^-1):Q', title='Wavenumber (cm^-1)', scale=alt.Scale(reverse=True)),
            y=alt.Y('Background Spectra:Q', title='Background Spectra'),
            color='File:N'
        ).properties(
            width=600,
            height=400
        )
        # Display the background signal graph
        st.subheader("Background Signal Graph")
        st.altair_chart(background_line_plot, use_container_width=True)






# Section 3: Processed files and download buttons
with col3:
  
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
    
