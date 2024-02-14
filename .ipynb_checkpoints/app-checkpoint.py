import streamlit as st
import pandas as pd
import plotly.express as px


def plotly_bar_chart(data, x, y, title, labels):
    # Calculate plot height dynamically: base_height for plot area plus a height for each bar
    base_height = 250
    height_per_bar = 35
    height = base_height + (height_per_bar * data.shape[0])
    
    fig = px.bar(
        data,
        x=x,
        y=y,
        text=x, # Display the count on bars
        orientation='h', # Horizontal bar chart
        labels=labels,
        title=title
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'}, # Ensure categories are sorted by value
        xaxis_title=labels['x'],
        yaxis_title=labels['y'],
        height=height, # Set dynamic height
        hovermode="y unified" # Unify hover label format
    )
    fig.update_traces(texttemplate='%{text}', textposition='inside') # Update text format
    return fig

def page_firm_selection(out, cluster_text):
    st.title("Clusters in Firms")

    # Sidebar - Firm selection
    selected_firm = st.sidebar.selectbox("Select a firm:", out['firm'].unique())

    # Plot barplot for selected firm
    st.subheader(f"Number of patents for {selected_firm} in each cluster")
    firm_data = out[out['firm'] == selected_firm].merge(cluster_text, on='cluster_id')
    firm_data = firm_data.sort_values(by='n_patents')

    fig_firm = plotly_bar_chart(firm_data, 'n_patents', 'words',
                                title=f"Number of patents for {selected_firm} in each cluster",
                                labels={'x': "Number of Patents", 'y': "Cluster Words"}
                                )
    st.plotly_chart(fig_firm)

def page_cluster_selection(out, cluster_text):
    st.title("Firms in clusters")

    # Sidebar - Cluster selection
    selected_cluster = st.sidebar.selectbox("Select a cluster:", cluster_text['words'].unique())

    # Plot barplot for selected cluster
    #st.subsubheader(f"Number of patents for each firm in cluster whose top 10 words are:")
    #st.subheader(f"{selected_cluster}")
    
    # Main header description
    st.subheader(f"Number of patents for each firm in cluster whose top 10 words are:")

    # Display top words in a larger font
    st.markdown(f"<span style='font-size: 1.5em;'>{selected_cluster}</span>", unsafe_allow_html=True)

    cluster_data = cluster_text[cluster_text['words'] == selected_cluster].merge(out, on='cluster_id')
    cluster_data = cluster_data.sort_values(by='n_patents')

    fig_cluster = plotly_bar_chart(cluster_data, 'n_patents', 'firm',
                                   title=f"Number of patents in cluster",
                                   labels={'x': "Number of Patents", 'y': "Firms"}
                                   )
    st.plotly_chart(fig_cluster)

def page_cluster_firm_count(out, cluster_text):
    st.title("Cluster Firm Count Analysis")
    
    st.subheader("Number of firms within each cluster")
    
    # Group by cluster_id, count unique firms per cluster
    cluster_firm_count = out.groupby('cluster_id')['firm'].nunique().reset_index()
    cluster_firm_count = cluster_firm_count.merge(cluster_text, on='cluster_id')[:50]
    
    # Create a new figure
    fig = plotly_bar_chart(
        cluster_firm_count, 
        'firm', 
        'words',
        " ",
        {'x': "Number of Firms", 'y': "Cluster"}
    )
    
    st.plotly_chart(fig)

# Main function to control the flow of the app
def main(out, cluster_text):


    unique_n_clusters = sorted(out['n_clusters'].unique())
    selected_n_clusters = st.sidebar.selectbox("Select the number of clusters:", unique_n_clusters)

    total = cluster_text['cluster_id'].max()
    st.sidebar.title(f'Total Number of Clusters: {selected_n_clusters}')

    # Filter the dataframes based on the selected number of clusters
    filtered_out = out[out['n_clusters'] == selected_n_clusters]
    filtered_cluster_text = cluster_text[cluster_text['n_clusters'] == selected_n_clusters]

    page = st.sidebar.radio("Go to", ('See all Clusters','Firm Selection', 'Cluster Selection'))

    if page == 'Firm Selection':
        page_firm_selection(filtered_out, filtered_cluster_text)
    elif page == 'Cluster Selection':
        page_cluster_selection(filtered_out, filtered_cluster_text)
    elif page == 'See all Clusters':
        page_cluster_firm_count(filtered_out, filtered_cluster_text)

if __name__ == "__main__":
    # Make sure you load your data before calling main
    out = pd.read_csv('./data/out.csv')
    cluster_text = pd.read_csv('./data/clusters.csv')
    main(out, cluster_text)