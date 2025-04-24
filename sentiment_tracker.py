# Streamlit dashboard for multi-sector industry sentiment from Excel file with quarterly sentiment view
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Sheet setup
FILE_PATH = "./Sentiment Tracker.xlsx"
SHEET_NAME = "Sentiment Tracker"  # Name of the sheet in the Excel file

# Connect and load data from Excel file
def load_sheet_data():
    # Load data from an Excel file
    df = pd.read_excel(FILE_PATH)
    # Add error handling for invalid date formats
    try:
        # Check if the 'Date' column exists
        if 'Date' not in df.columns:
            raise ValueError("The 'Date' column is missing from the Excel file. Please ensure the column exists and is named correctly.")
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Convert invalid dates to NaT (Not a Time)
        if df['Date'].isna().any():
            raise ValueError("Some dates could not be parsed. Please check the 'Date' column in the Excel file.")
    except Exception as e:
        raise ValueError(f"Error processing the 'Date' column: {e}")
    
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)  # Group dates into calendar quarters
    return df

# Sentiment scoring map for visualization
SENTIMENT_SCORE = {
    "Bearish": -2,
    "Inflection to Bearish": -1,
    "Neutral": 0,
    "Inflection to Bullish": 1,
    "Bullish": 2
}

# Load data
st.title("📊 Quarterly Sector Sentiment Tracker")
st.markdown("This dashboard visualizes industry sentiment across sectors, based on expert assessments submitted via Google Sheets.")

try:
    data = load_sheet_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Apply sentiment scoring
data['Score'] = data['Sentiment'].map(SENTIMENT_SCORE)

# Filters
sector_filter = st.multiselect("Select sector(s):", data['Sector'].unique(), default=data['Sector'].unique())
quarter_filter = st.multiselect("Select quarter(s):", sorted(data['Quarter'].unique()), default=sorted(data['Quarter'].unique()))

filtered = data[
    data['Sector'].isin(sector_filter) &
    data['Quarter'].isin(quarter_filter)
]

# Table view
st.subheader("📋 Sentiment Table")
st.dataframe(filtered.sort_values(by="Date", ascending=False))

# Heatmap view
st.subheader("📈 Sentiment Score by Quarter & Sector")
heatmap_data = filtered.groupby(['Quarter', 'Sector'])['Score'].mean().reset_index()

# Map scores to their descriptors for the heatmap legend
heatmap_data['Sentiment Descriptor'] = heatmap_data['Score'].map({
    -2: "Bearish",
    -1: "Inflection to Bearish",
     0: "Neutral",
     1: "Inflection to Bullish",
     2: "Bullish"
})

# Update the heatmap to use sentiment descriptors directly in the legend
fig = px.density_heatmap(
    heatmap_data, x='Quarter', y='Sector', z='Sentiment Descriptor',
    color_continuous_scale=['red', 'orange', 'white', 'lightgreen', 'green'],
    title="Average Sentiment by Sector per Quarter",
    labels={"Sentiment Descriptor": "Sentiment"}  # Update legend label
)
st.plotly_chart(fig, use_container_width=True)

# Optional: Quotes or notes column display
if 'Notes' in data.columns:
    st.subheader("🗣 Notes")
    for _, row in filtered.iterrows():
        st.markdown(f"**{row['Sector']} | {row['Quarter']}** | *{row['Sentiment']}* | {row['Date'].strftime('%b %d, %Y')}")
        st.markdown(f"> {row['Notes']}")
