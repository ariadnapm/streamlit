import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to APEM MDev PAT MiniSite! 👋")

st.sidebar.success("Select a tool you would like to try!")

st.markdown(
    """
    I (APEM) created this site that contains different tools that might be useful for the members of the PAT team.
    **👈 Select a tool from the sidebar:
    of what Streamlit can do!
    ### Are you working with chromatograms?
    - Do you want to view plots? Go [here](https://github.com/ariadnapm/streamlit/blob/main/chromatogram_plotter.py)
    ### Do you need to work with OPUS files?
    - Convert them into easy to understand Excel files, using this [tool](https://github.com/ariadnapm/streamlit/blob/main/OPUS_converter.py)
    ### Do you have funny formats as files?
    - Do you just want to convert text and other formatted files into ".xlsx" files? Click [here](https://github.com/ariadnapm/streamlit/blob/main/clean_all_files.py)
"""
)
