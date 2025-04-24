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

# Debugging output to inspect the loaded columns
st.write("Loaded columns:", data.columns)  # Display the columns in the data DataFrame for debugging

# Apply sentiment scoring
data['Score'] = data['Sentiment'].map(SENTIMENT_SCORE)

# Adjust the dates in the Excel file to the previous quarter before creating the 'Quarter' column
data['Date'] = data['Date'] - pd.offsets.QuarterEnd(1)
data['Quarter'] = data['Date'].dt.to_period('Q').astype(str)  # Group dates into calendar quarters

# Filters
sector_filter = st.multiselect(
    "Select sector(s):", 
    ["Consumer", "Financials", "Hardware", "Healthcare", "Ind/Transportation", "Ind/Housing", "Ind/Building Products", "Software", "TMT", "Utilities"], 
    default=["Consumer", "Financials", "Hardware", "Healthcare", "Ind/Transportation", "Ind/Housing", "Ind/Building Products", "Software", "TMT", "Utilities"]
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

# Map scores to their descriptors for the heatmap legend
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
