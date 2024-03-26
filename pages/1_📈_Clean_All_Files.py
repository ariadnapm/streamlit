import streamlit as st
import pandas as pd
from openpyxl.comments import Comment
from io import BytesIO
import os

st.set_page_config(page_title="File Upload and Processing", page_icon="📈", layout="wide")
st.sidebar.header("File Upload and Processing")


# Title and file upload
st.markdown('# File Upload and Processing')
input_files = st.file_uploader("Upload your files", accept_multiple_files=True)


# Processing the uploaded files
if input_files:
    for file in input_files:
        # Read the data file into a Pandas DataFrame
        df = pd.read_fwf(file)
        df_info = df.iloc[0:3]
        df = df.iloc[6:]
        
        # Remove "#" and space from each line that has it
        df = df.applymap(lambda x: x.replace("#	", "") if isinstance(x, str) else x)

        # Drop the rows starting with "V" and its next row
        rows_to_drop = []
        for i, row in df.iterrows():
            if str(row[0]).startswith("V"):
                rows_to_drop.append(i)
                if i+1 < df.shape[0]:
                    rows_to_drop.append(i+1)
        df.drop(rows_to_drop, axis=0, inplace=True)
        df.columns = ["Software Empower 3 Software Build 3471	Afd. 403, DAPI Support QC"]

        # Text file info
        sample_info = df_info.iloc[0]
        user_info = df_info.iloc[1]
        system_info = df_info.iloc[2]

        info = sample_info + user_info + system_info

        # Split column by "\t"
        df = df["Software Empower 3 Software Build 3471	Afd. 403, DAPI Support QC"].str.split("\t", n=10, expand=True).rename(columns={0:"#", 1: "Vial", 2:"LV_SampleInfo", 3:"SampleName", 4:"Name", 5: "RT Ratio", 6:"RT", 7:"% Area", 8:"Area", 9:"Amount", 10:"Units_Unknown"})

        output_file_name = file.name.split('.')[0] + '_cleaned.xlsx'
        df.to_excel(output_file_name, index=False)

        # Write the cleaned data and df_info to the Excel file
        with pd.ExcelWriter(output_file_name, engine='openpyxl') as writer:
            # Write the cleaned data to the first sheet
            df.to_excel(writer, sheet_name='Sheet1', index=False)

            # Add a comment to cell N2
            sheet = writer.book['Sheet1']
            cell = sheet.cell(row=2, column=14)
            comment = Comment(info, "user")
            cell.comment = comment

        # Offer the file for download
        with open(output_file_name, 'rb') as f:
            bytes_data = BytesIO(f.read())
        st.download_button(
            label="Download Processed File",
            data=bytes_data,
            file_name=output_file_name,
            mime="application/octet-stream"
        )
