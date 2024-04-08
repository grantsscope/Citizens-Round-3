import pandas as pd
import numpy as np
import hdbscan
from umap import UMAP
from sentence_transformers import SentenceTransformer
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text


# Load your CSV file
df = pd.read_csv('summarized_cr3_projects.csv')

# Ensure all descriptions are strings
df['Project Desc'] = df['Project Desc'].astype(str)

# Load a pre-trained model (e.g., all-MiniLM-L6-v2 for efficiency)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for the project descriptions
embeddings = model.encode(df['Project Desc'].tolist(), show_progress_bar=True)

# Reduce dimensionality for clustering
umap_model = UMAP(n_neighbors=15, n_components=2, metric='cosine')
reduced_embeddings = umap_model.fit_transform(embeddings)

# Cluster using HDBSCAN
cluster = hdbscan.HDBSCAN(min_cluster_size=4, metric='euclidean', cluster_selection_method='eom').fit(reduced_embeddings)



# Prepare the DataFrame for Plotly
plot_df = pd.DataFrame(reduced_embeddings, columns=['UMAP_1', 'UMAP_2'])
plot_df['Cluster'] = cluster.labels_
plot_df['Project Name'] = df['Project Name']
plot_df['Project Desc'] = df['Project Desc']
plot_df['Short Project Desc'] = df['Short Project Desc']
plot_df['PayoutAddress'] = df['PayoutAddress']

plot_df.to_csv('cluster_cr3_projects.csv')

# Adjust the project descriptions to add a new line after each full stop and truncate to the first 300 characters
#plot_df['Project Desc Short'] = plot_df['Project Desc'].apply(lambda x: x.replace('. ', '.\n')[:300])

# Create an interactive scatter plot using Plotly Express
fig = px.scatter(plot_df, x='UMAP_1', y='UMAP_2', color='Cluster',
                 text='Project Name', 
                 hover_data={'UMAP_1': False, 'UMAP_2': False, 'Project Name': False, 'Short Project Desc': True, 'Cluster': False},
                 title='HDBSCAN Clustering with UMAP Reduction',
                 color_continuous_scale=px.colors.sequential.Bluered)

# Update layout to ensure text labels are displayed nicely
fig.update_traces(textposition='top center')

fig.show()
