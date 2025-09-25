import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- Set up the Streamlit page configuration ---
# This must be the first Streamlit command.
st.set_page_config(
    page_title="CORD-19 Research Paper Explorer",
    page_icon="📄",
    layout="wide"
)

# --- Data Loading and Caching ---
# Use st.cache_data to cache the function's output.
# This ensures data is loaded only once, improving performance.
@st.cache_data(show_spinner="Loading and cleaning data...")
def load_data():
    """
    Loads the metadata from the CORD-19 dataset, cleans it, and returns a DataFrame.
    """
    try:
        df = pd.read_csv("metadata.csv", low_memory=False)
        # Select relevant columns
        df = df[['title', 'abstract', 'publish_time', 'authors', 'journal']]
        
        # Convert 'publish_time' to datetime objects, coercing errors
        df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
        
        # Extract the year for analysis
        df['year'] = df['publish_time'].dt.year
        
        # Drop rows where 'title' or 'abstract' is missing
        return df.dropna(subset=['title', 'abstract'])
        
    except FileNotFoundError:
        st.error("Error: 'metadata.csv' not found. Please ensure the file is in the same directory.")
        return pd.DataFrame() # Return an empty DataFrame on error

df = load_data()

# Check if data loaded successfully before proceeding
if not df.empty:
    
    # --- Main Application Title and Description ---
    st.title("CORD-19 Research Paper Explorer")
    st.markdown("Dive into the CORD-19 dataset to explore publications on COVID-19 and related research.")

    # --- Sidebar for Filters and Controls ---
    st.sidebar.header("App Controls")
    
    # Checkbox to show raw data
    if st.sidebar.checkbox("Show raw data"):
        st.subheader("Raw Data Sample")
        st.write(df.head(20))
        st.info(f"Total papers in dataset: **{len(df)}**")

    # --- Main Content Area ---
    # Create columns for a two-plot layout
    col1, col2 = st.columns(2)
    
    # --- Publications per Year Plot ---
    with col1:
        st.subheader("Publications per Year")
        # Use .value_counts() and .sort_index() to get counts per year
        papers_per_year = df['year'].value_counts().sort_index()

        # Set a professional style for the plot
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x=papers_per_year.index, y=papers_per_year.values, ax=ax)
        
        # Customize plot labels and title
        ax.set_title("Number of Papers Published by Year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Number of Publications")
        fig.tight_layout() # Adjust layout to prevent labels from overlapping
        st.pyplot(fig)
        
    # --- Top Journals Plot ---
    with col2:
        st.subheader("Top 10 Journals")
        # Get the top 10 journals by publication count
        top_journals = df['journal'].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_journals.values, y=top_journals.index, ax=ax, palette="viridis")
        
        # Customize plot labels and title
        ax.set_title("Top 10 Journals by Publication Count")
        ax.set_xlabel("Number of Publications")
        ax.set_ylabel("Journal")
        fig.tight_layout()
        st.pyplot(fig)
        
    # --- Search Papers Section ---
    st.subheader("Search Papers by Keyword")
    keyword = st.text_input(
        "Enter a keyword (e.g., vaccine, transmission, mRNA)", 
        placeholder="Enter your keyword here..."
    )
    
    # Use a button to trigger the search explicitly
    if st.button("Search") and keyword:
        # Use .str.contains() for case-insensitive keyword search
        results = df[df['title'].str.contains(keyword, case=False, na=False)]
        
        if not results.empty:
            st.success(f"Found {len(results)} papers related to '{keyword}'.")
            st.dataframe(results[['title', 'authors', 'year', 'journal']].head(20))
        else:
            st.warning(f"No papers found for the keyword '{keyword}'. Try a different term.")

# --- Conclusion for the user ---
# This part is outside the main app logic and serves as a friendly message.
st.markdown("---")
st.markdown("Developed with Streamlit by a large language model.")
st.markdown("Data source: CORD-19 dataset")

