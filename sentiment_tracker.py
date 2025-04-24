# Streamlit dashboard for multi-sector industry sentiment with color gradient sentiment visualization
import streamlit as st
import pandas as pd
import plotly.express as px
import docx2txt
import io

# Load initial data (can be extended with Google Sheets or CSV)
def load_initial_data():
    return pd.DataFrame([
        {"Sector": "Concrete", "Topic": "Demand", "Date": "2025-04-14", "Sentiment": "Positive", "Quote": "Strong backlog built in late 2024 and early 2025 underpinned growth...", "Source": "Q1’25 Recap"},
        {"Sector": "Concrete", "Topic": "Demand", "Date": "2025-02-04", "Sentiment": "Positive", "Quote": "Large-scale industrial projects... have accelerated and are the main drivers…", "Source": "Q4’24 & 2025 Outlook"},
        {"Sector": "Concrete", "Topic": "Volume", "Date": "2025-04-14", "Sentiment": "Positive", "Quote": "Ready-mix volume growth exceeded expectations by MSD%, up ~10% YoY…", "Source": "Q1’25 Recap"},
        {"Sector": "Concrete", "Topic": "Volume", "Date": "2025-02-04", "Sentiment": "Positive", "Quote": "Ready-mix concrete volumes up 10% and full-year volume 10%-15% higher y/y.", "Source": "Q4’24 & 2025 Outlook"},
        {"Sector": "Concrete", "Topic": "Pricing", "Date": "2025-04-14", "Sentiment": "Slightly Positive", "Quote": "Pricing is up around $5 per cubic yard YoY at the lower end but stable at the higher end.", "Source": "Q1’25 Recap"},
        {"Sector": "Concrete", "Topic": "Pricing", "Date": "2025-02-04", "Sentiment": "Slightly Positive", "Quote": "2025 could see more noticeable price hikes of $5-$10 per cubic yard...", "Source": "Q4’24 & 2025 Outlook"},
        {"Sector": "Concrete", "Topic": "Macro Headwinds", "Date": "2025-04-14", "Sentiment": "Mixed", "Quote": "Tariffs are the primary near-term risk... Labor workforce expansion is the next biggest headwind.", "Source": "Q1’25 Recap"},
        {"Sector": "Concrete", "Topic": "Macro Headwinds", "Date": "2025-02-04", "Sentiment": "Mixed", "Quote": "Labor remains the primary headwind... interest rates will delay residential recovery.", "Source": "Q4’24 & 2025 Outlook"},
    ])

# Basic GPT-style sentiment extractor (stubbed — replace with actual model/API call)
def extract_sentiment_from_text(text, sector):
    return pd.DataFrame([
        {"Sector": sector, "Topic": "Demand", "Date": pd.Timestamp("2025-05-01"), "Sentiment": "Positive", "Quote": "Example extracted sentiment for demand.", "Source": "Uploaded Note"},
        {"Sector": sector, "Topic": "Pricing", "Date": pd.Timestamp("2025-05-01"), "Sentiment": "Neutral", "Quote": "Example pricing sentiment extracted.", "Source": "Uploaded Note"},
    ])

# Sentiment mapping to numeric score for gradient chart
def map_sentiment_to_score(sent):
    score_map = {
        "Very Positive": 2,
        "Positive": 1,
        "Slightly Positive": 0.5,
        "Neutral": 0,
        "Mixed": 0,
        "Slightly Negative": -0.5,
        "Negative": -1,
        "Very Negative": -2
    }
    return score_map.get(sent, 0)

# App setup
st.title("📊 Multi-Sector Industry Sentiment Tracker")
st.markdown("Analyze expert sentiment across sectors and upload new transcripts for processing.")

# Load initial data
data = load_initial_data()

# Upload new file and process
uploaded_file = st.file_uploader("Upload a .docx transcript to process", type=["docx"])
sector_input = st.text_input("Enter the sector for this file (e.g., Staffing, Trucking, Dental)")
if uploaded_file and sector_input:
    with st.spinner("Processing uploaded file..."):
        text = docx2txt.process(uploaded_file)
        new_data = extract_sentiment_from_text(text, sector_input)
        data = pd.concat([data, new_data], ignore_index=True)
        st.success("Sentiment extracted and added!")

# Filter UI
data['Date'] = pd.to_datetime(data['Date'])
data['Score'] = data['Sentiment'].apply(map_sentiment_to_score)
sector_filter = st.multiselect("Select sector(s):", data['Sector'].unique(), default=data['Sector'].unique())
topic_filter = st.multiselect("Select topic(s):", data['Topic'].unique(), default=data['Topic'].unique())
date_range = st.date_input("Select date range:", [data['Date'].min().date(), data['Date'].max().date()])
if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

# Filtered view
filtered = data[
    data['Sector'].isin(sector_filter) &
    data['Topic'].isin(topic_filter) &
    data['Date'].dt.date.between(start_date, end_date)
]

# Table
st.subheader("📋 Sentiment Table")
st.dataframe(filtered.sort_values(by="Date", ascending=False))

# Chart: Heatmap-style with sentiment score coloring
st.subheader("📈 Average Sentiment Score by Topic & Sector")
avg_sent = filtered.groupby(['Sector', 'Topic'])['Score'].mean().reset_index()
fig = px.density_heatmap(
    avg_sent, x='Topic', y='Sector', z='Score',
    color_continuous_scale=['red', 'orange', 'white', 'lightgreen', 'green'],
    range_color=(-2, 2), title="Sentiment Score Heatmap"
)
st.plotly_chart(fig, use_container_width=True)

# Quotes
st.subheader("🗣 Quotes")
for _, row in filtered.iterrows():
    st.markdown(f"**{row['Sector']} | {row['Topic']}** | *{row['Sentiment']}* | {row['Date'].strftime('%b %d, %Y')} - {row['Source']}")
    st.markdown(f"> {row['Quote']}")