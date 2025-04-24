# Streamlit dashboard for multi-sector industry sentiment from Excel file with quarterly sentiment view
import streamlit as st
import pandas as pd
import altair as alt

# Sheet setup
FILE_PATH = "./Sentiment Tracker.xlsx"
SHEET_NAME = "Sentiment Tracker"

# Sentiment scoring map
SENTIMENT_SCORE = {
    "Bearish": -2,
    "Inflection to Bearish": -1.5,
    "Neutral - Cautious Outlook": -1,
    "Neutral": 0,
    "Neutral - Bullish Outlook": 1,
    "Inflection to Bullish": 1.5,
        "Bullish": 2,
    }

# Load data function
def load_sheet_data():
    df = pd.read_excel(FILE_PATH)
    df['Score'] = df['Sentiment'].map(SENTIMENT_SCORE)
    df = df.dropna(subset=['Score', 'Date', 'Sector', 'Sentiment'])
    df['Date'] = df['Date'] - pd.offsets.QuarterEnd(1)
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    return df


# Load data
st.title("\U0001F4CA Quarterly Sector Sentiment Tracker")
st.markdown("This dashboard visualizes industry sentiment across sectors based on our conversations with industry experts.")

try:
    data = load_sheet_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Filters
sector_filter = st.multiselect("Select sector(s):", sorted(data['Sector'].dropna().unique()), default=sorted(data['Sector'].dropna().unique()))
quarter_filter = st.multiselect("Select quarter(s):", sorted(data['Quarter'].unique()), default=sorted(data['Quarter'].unique()))

filtered = data[data['Sector'].isin(sector_filter) & data['Quarter'].isin(quarter_filter)]

# Table view
st.subheader("\U0001F4CB Sentiment Table")
st.dataframe(filtered.sort_values(by="Date", ascending=False))

# Heatmap view
st.subheader("\U0001F4C8 Sentiment Score by Quarter & Sector")
heatmap_data = filtered.groupby(['Quarter', 'Sector'])['Score'].mean().reset_index()
heatmap_data = heatmap_data.dropna(subset=['Score'])


# Ensure no sentiment labels are included in the heatmap
heatmap_data = heatmap_data.drop(columns=['Sentiment Descriptor'], errors='ignore')  # Remove any lingering sentiment label columns

# Remove sentiment labels from the heatmap and use numeric scores
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X('Quarter:O', title='Quarter'),
    y=alt.Y('Sector:O', title='Sector'),
    color=alt.Color('Score:Q', scale=alt.Scale(domain=[-2, 2], scheme='redyellowgreen'), title='Average Sentiment')
).properties(
    title="Average Sentiment by Sector per Quarter",
    width=600,
    height=400
)

st.altair_chart(heatmap, use_container_width=True)

# Line chart: sentiment trend over time by sector
trend_data = filtered.groupby(['Quarter', 'Sector'])['Score'].mean().reset_index()
line_chart = alt.Chart(trend_data).mark_line(point=True).encode(
    x=alt.X('Quarter:O', title='Quarter'),
    y=alt.Y('Score:Q', title='Avg Sentiment Score', scale=alt.Scale(domain=[-2, 2])),
    color='Sector:N',
    tooltip=['Quarter', 'Sector', 'Score']
).properties(
    title="Sentiment Trends by Sector",
    width=700,
    height=400
)

st.altair_chart(line_chart, use_container_width=True)

# Optional: Notes display
if 'Notes' in data.columns:
    st.subheader("\U0001F5E3 Notes")
    for _, row in filtered.iterrows():
        st.markdown(f"**{row['Sector']} | {row['Quarter']}** | *{row['Sentiment']}* | {row['Date'].strftime('%b %d, %Y')}")
        st.markdown(f"> {row['Notes']}")
