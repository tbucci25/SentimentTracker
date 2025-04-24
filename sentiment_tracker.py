# Streamlit dashboard for multi-sector industry sentiment from Excel file with quarterly sentiment view
import streamlit as st
import pandas as pd
import altair as alt
import os

# Sheet setup
FILE_PATH = "./Sentiment Tracker.xlsx"
SHEET_NAME = "Sentiment Tracker"  # Name of the sheet in the Excel file

# Connect and load data from Excel file
def load_sheet_data():
    # Load data from an Excel file
    df = pd.read_excel(FILE_PATH)
    df['Score'] = df['Sentiment'].map(SENTIMENT_SCORE)
    df = df.dropna(subset=['Score', 'Date', 'Sector', 'Sentiment'])  # Exclude rows with null values
    df['Date'] = df['Date'] - pd.offsets.QuarterEnd(1)  # Adjust dates to the previous quarter
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)  # Group dates into calendar quarters
    return df
  
# Update the sentiment scoring map to the specified levels
SENTIMENT_SCORE = {
    "Bearish": -2,
    "Inflection to Bearish": -1.5,
    "Neutral - Cautious Outlook": -1,
    "Neutral": 0,
    "Neutral - Bullish Outlook": 1,
    "Inflection to Bullish": 1.5,
    "Bullish": 2
}

# Load data
st.title("📊 Quarterly Sector Sentiment Tracker")
st.markdown("This dashboard visualizes industry sentiment across sectors based on our conversations with indsutry experts.")

try:
    data = load_sheet_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Filters
sector_filter = st.multiselect(
    "Select sector(s):", 
    sorted(data['Sector'].dropna().unique()),  # Dynamically fetch unique sectors from the data
    default=sorted(data['Sector'].dropna().unique())  # Set default to all available sectors
)
quarter_filter = st.multiselect("Select quarter(s):", sorted(data['Quarter'].unique()), default=sorted(data['Quarter'].unique()))

filtered = data[
    data['Sector'].isin(sector_filter) &
    data['Quarter'].isin(quarter_filter)
]

# Table view
st.subheader("📋 Sentiment Table")
st.dataframe(filtered.sort_values(by="Date", ascending=False))

# Heatmap view using Altair
st.subheader("📈 Sentiment Score by Quarter & Sector")
heatmap_data = filtered.groupby(['Quarter', 'Sector'])['Score'].mean().reset_index()

# Ensure all scores are mapped and exclude null values
heatmap_data = heatmap_data.dropna(subset=['Score'])
heatmap_data['Sentiment Descriptor'] = heatmap_data['Score'].map({
    -2: "Bearish",
    -1.5: "Inflection to Bearish",
    -1: "Neutral - Cautious Outlook",
     0: "Neutral",
     1: "Neutral - Bullish Outlook",
     1.5: "Inflection to Bullish",
     2: "Bullish"
})

# Ensure there is no null data in the heatmap by filtering out rows with null values
heatmap_data = heatmap_data.dropna(subset=['Score', 'Sector', 'Quarter'])

# Update the Altair heatmap to use sentiment descriptors for the color encoding
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X('Quarter:O', title='Quarter'),
    y=alt.Y('Sector:O', title='Sector'),
    color=alt.Color('Sentiment Descriptor:N', scale=alt.Scale(scheme='redyellowgreen'), title='Sentiment')
).properties(
    title="Average Sentiment by Sector per Quarter",
    width=600,
    height=400
)

st.altair_chart(heatmap, use_container_width=True)

# Optional: Quotes or notes column display
if 'Notes' in data.columns:
    st.subheader("🗣 Notes")
    for _, row in filtered.iterrows():
        st.markdown(f"**{row['Sector']} | {row['Quarter']}** | *{row['Sentiment']}* | {row['Date'].strftime('%b %d, %Y')}")
        st.markdown(f"> {row['Notes']}")
