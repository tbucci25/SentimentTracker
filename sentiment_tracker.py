# Streamlit dashboard for sentiment tracking
import streamlit as st
import pandas as pd
import plotly.express as px

# Data
sentiment_data = pd.DataFrame([
    {"Topic": "Demand", "Date": "2025-04-14", "Sentiment": "Positive", "Quote": "Strong backlog built in late 2024 and early 2025 underpinned growth...", "Source": "Q1’25 Recap"},
    {"Topic": "Demand", "Date": "2025-02-04", "Sentiment": "Positive", "Quote": "Large-scale industrial projects... have accelerated and are the main drivers…", "Source": "Q4’24 & 2025 Outlook"},
    {"Topic": "Volume", "Date": "2025-04-14", "Sentiment": "Positive", "Quote": "Ready-mix volume growth exceeded expectations by MSD%, up ~10% YoY…", "Source": "Q1’25 Recap"},
    {"Topic": "Volume", "Date": "2025-02-04", "Sentiment": "Positive", "Quote": "Ready-mix concrete volumes up 10% and full-year volume 10%-15% higher y/y.", "Source": "Q4’24 & 2025 Outlook"},
    {"Topic": "Pricing", "Date": "2025-04-14", "Sentiment": "Slightly Positive", "Quote": "Pricing is up around $5 per cubic yard YoY at the lower end but stable at the higher end.", "Source": "Q1’25 Recap"},
    {"Topic": "Pricing", "Date": "2025-02-04", "Sentiment": "Slightly Positive", "Quote": "2025 could see more noticeable price hikes of $5-$10 per cubic yard...", "Source": "Q4’24 & 2025 Outlook"},
    {"Topic": "Macro Headwinds", "Date": "2025-04-14", "Sentiment": "Mixed", "Quote": "Tariffs are the primary near-term risk... Labor workforce expansion is the next biggest headwind.", "Source": "Q1’25 Recap"},
    {"Topic": "Macro Headwinds", "Date": "2025-02-04", "Sentiment": "Mixed", "Quote": "Labor remains the primary headwind... interest rates will delay residential recovery.", "Source": "Q4’24 & 2025 Outlook"},
])

sentiment_data['Date'] = pd.to_datetime(sentiment_data['Date'])

# Streamlit UI
st.title("🧱 Industry Sentiment Tracker")
st.markdown("Filter and explore sentiment by topic, time, and source.")

# Filters
topic_filter = st.multiselect("Select topic(s):", sentiment_data['Topic'].unique(), default=sentiment_data['Topic'].unique())
date_range = st.date_input("Select date range:", [sentiment_data['Date'].min(), sentiment_data['Date'].max()])

# Filtered data
filtered_data = sentiment_data[
    sentiment_data['Topic'].isin(topic_filter) &
    sentiment_data['Date'].between(date_range[0], date_range[1])
]

# Display table
st.subheader("🔍 Sentiment Table")
st.dataframe(filtered_data.sort_values(by="Date", ascending=False))

# Sentiment breakdown chart
st.subheader("📊 Sentiment Breakdown")
fig = px.histogram(filtered_data, x="Topic", color="Sentiment", barmode="group", title="Sentiment by Topic")
st.plotly_chart(fig, use_container_width=True)

# Quote preview
st.subheader("💬 Supporting Quotes")
for _, row in filtered_data.iterrows():
    st.markdown(f"**{row['Topic']}** | *{row['Sentiment']}* | {row['Date'].strftime('%b %d, %Y')} - {row['Source']}")
    st.markdown(f"> {row['Quote']}")
