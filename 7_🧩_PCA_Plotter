import pandas as pd
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.graph_objects as go

st.set_page_config(page_title="PCA show", page_icon="🧩", layout="wide")

st.markdown('# PCA show')

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

def perform_pca(csv_file):
    df = pd.read_csv(csv_file, header=0)
    features = df.columns.tolist()
    colour_in_col = df.columns.get_loc('colour')
    features = df.columns[0:colour_in_col]
    features_show = features[:]
    x = df.loc[:, features].values
    
    # Standardizing the features
    x = StandardScaler().fit_transform(x)
    pca = PCA(n_components=2)
    principalComponents = pca.fit_transform(x)
    principalDf = pd.DataFrame(data=principalComponents, columns=['principal component 1', 'principal component 2'])
    finalDf = pd.concat([principalDf, df[['colour']]], axis=1)
    
    scaler_df = finalDf[['principal component 1','principal component 2']]
    scaler = 1 / (scaler_df.max()-scaler_df.min())
    pca_df_scaled = scaler_df.copy()
    
    for index in scaler.index:
        pca_df_scaled[index] *= scaler[index]

    explain_PCone = round(pca.explained_variance_ratio_[0]*100,1)
    explain_PCtwo = round(pca.explained_variance_ratio_[1]*100,1)
    explain_total = explain_PCone + explain_PCtwo

    loadings = pca.components_
    xs = loadings[0]
    ys = loadings[1]

    fig = go.Figure()

    # Create a dynamic color map based on unique values in the 'colour' column
    unique_colors = finalDf['colour'].unique()
    color_map = px.colors.qualitative.Alphabet[:len(unique_colors)]

    #the arrows
    for i, varnames in enumerate(features_show):
        fig.add_trace(go.Scatter(x=[0,xs[i]],
                                 y=[0,ys[i]],
                                 mode = "lines+markers+text",
                                 marker= dict(size=10,
                                              symbol= "arrow",
                                              color= "black",
                                              angleref="previous"),
                                 name = varnames,
                                 text=varnames,
                                 textposition='top right',
                                )
                    )
    #the points
    for i, color in enumerate(unique_colors):
        indicesToKeep = finalDf['colour'] == color
        fig.add_trace(go.Scatter(x=pca_df_scaled.loc[indicesToKeep, 'principal component 1'], 
                                 y=pca_df_scaled.loc[indicesToKeep, 'principal component 2'],
                                 mode="markers",
                                 marker=dict(color=color_map[i], size=10),
                                 name=str(color)
                                )
                    )   

    for i in range(0, len(features_show)):
        if (not features_show[i] in unique_colors):
            fig["data"][i]["showlegend"] = False


    fig.update_xaxes(showgrid=True, automargin = True)
    fig.update_yaxes(showgrid=True)
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        width=1000,
        height=1000,
        title= '2 Component PCA, '+str(explain_total)+' %',
        title_x=0.5,
        xaxis_title='Principal Component 1, '+str(explain_PCone)+' %',
        yaxis_title='Principal Component 2, '+str(explain_PCtwo)+' %',
        showlegend=True
    )
    return fig


def main():
    with st.container():  
        uploaded_files = st.file_uploader("Upload (CSV) Files", accept_multiple_files=True)
        if uploaded_files:
            for file in uploaded_files:   
                try:
                    fig = perform_pca(file)
                    st.plotly_chart(fig, use_container_width=False, theme="streamlit")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

