# Streamlit dashboard for multi-sector industry sentiment from Google Sheet with quarterly sentiment view
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import re  # Added for extracting the sheet ID from the URL
from oauth2client.service_account import ServiceAccountCredentials

# Sheet setup
SHEET_LINK = "https://docs.google.com/spreadsheets/d/1UAhHj6wG9_Clc7obd4jOekUohK7ifV4NYETSqdqiWSY/edit#gid=0"  # Replace with your actual Google Sheet ID
SHEET_NAME = "Sentiment Tracker"  # Change if your tab has a different name

# Connect and load data from Google Sheet
def load_sheet_data():
    # Define the scope for accessing Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Authenticate with gspread using default credentials for public sheets
    credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
    gc = gspread.authorize(credentials)

    # Access the Google Sheet using its public URL
    sh = gc.open_by_url(SHEET_LINK)
    worksheet = sh.worksheet(SHEET_NAME)
    records = worksheet.get_all_records()  # Fetch all records as a list of dictionaries
    df = pd.DataFrame(records)  # Convert to a Pandas DataFrame
    df['Date'] = pd.to_datetime(df['Date'])
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
    st.error(f"Error loading Google Sheet data: {e}")
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
fig = px.density_heatmap(
    heatmap_data, x='Quarter', y='Sector', z='Score',
    color_continuous_scale=['red', 'orange', 'white', 'lightgreen', 'green'],
    range_color=(-2, 2), title="Average Sentiment by Sector per Quarter"
)
st.plotly_chart(fig, use_container_width=True)

# Optional: Quotes or notes column display
if 'Notes' in data.columns:
    st.subheader("🗣 Notes")
    for _, row in filtered.iterrows():
        st.markdown(f"**{row['Sector']} | {row['Quarter']}** | *{row['Sentiment']}* | {row['Date'].strftime('%b %d, %Y')}")
        st.markdown(f"> {row['Notes']}")
