import streamlit as st
import openai
import requests
import re
import random
import urllib.parse
from datetime import datetime

# Load secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

sponsor_lines = [
    "📣 Capsule Ads | Increase Your Business Visibility | https://wa.link/mwb2hf",
    "📣 Amazon | One-Stop Online Shopping | https://www.amazon.com",
    "📣 Flipkart | Fashion, Electronics & More | https://www.flipkart.com",
    "📣 Myntra | Trendy Fashion & Accessories | https://www.myntra.com",
    "📣 Blinkit | Instant Grocery & Essentials | https://www.blinkit.com",
    "📣 Sid's Farm | Pure & Fresh Dairy Products | https://www.sidsfarm.com",
    "📣 Nykaa | Beauty, Skincare & Cosmetics | https://www.nykaa.com",
    "📣 Urban Company | Home & Personal Services | https://www.urbancompany.com",
    "📣 Zomato | Online Food Delivery & Restaurants | https://www.zomato.com",
    "📣 Porter | Mini Truck & Bike Logistics | https://www.porter.in"
]

# List of supported countries
country_options = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "Singapore": "sg",
    "Germany": "de"
}

valid_query_pattern = re.compile(
    r"^Top 10 ([A-Za-z]+|[A-Za-z]+\s[A-Za-z]+) (News Today|[A-Za-z]+\sNews Today)$"
)

# UI
st.set_page_config(page_title="Capsule – Live News", layout="centered")
st.title("📰 Capsule – Live News Summarizer")

# Country select
selected_country = st.selectbox("🌍 Select Country", list(country_options.keys()), index=0)
country_code = country_options[selected_country]

with st.expander("📌 Accepted Formats"):
    st.markdown("""
    1. Top 10 **[Topic]** News Today  
       _Example: Top 10 Sports News Today_  
    2. Top 10 **[City Name]** News Today  
       _Example: Top 10 Delhi News Today_  
    3. Top 10 **[City Name] [Topic]** News Today  
       _Example: Top 10 Mumbai Politics News Today_
    """)

user_query = st.text_input("🔍 Your Query")

def is_valid_query(query):
    return bool(valid_query_pattern.match(query)) and all(ord(c) < 128 for c in query)

def extract_topic(query):
    return query.replace("Top 10", "").replace("News Today", "").strip()

def fetch_news(query, country):
    topic = extract_topic(query)
    url = f"https://newsapi.org/v2/top-headlines?q={topic}&country={country}&language=en&pageSize=10&apiKey={NEWS_API_KEY}"
    res = requests.get(url)
    articles = res.json().get("articles", [])
    return [
        {
            "title": a["title"],
            "description": a["description"] or "",
            "source": a["source"]["name"],
            "url": a["url"]
        }
        for a in articles if a["title"] and a["url"]
    ]

def format_summaries(query, articles):
    today = datetime.now().strftime("%B %d, %Y")
    sponsors = random.sample(sponsor_lines, 10)
    summaries = []

    for idx, (a, sponsor) in enumerate(zip(articles, sponsors), start=1):
        headline = a['title']
        summary = a['description'] or "No description available."
        read_more = f"[🔗 Read more – {a['source']}]({a['url']})"

        formatted = f"""
{idx}. {query} | {today}  
**{headline}**  
{summary}  
{read_more}  
{str(sponsor)}  
---
"""
        summaries.append(formatted.strip())

    summaries.append("✅ All 10 news checked—done for today! 🎯")
    return "\n\n".join(summaries)

def generate_share_links(summary_text):
    encoded_text = urllib.parse.quote(summary_text[:1500])  # truncate for platforms
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
    telegram_url = f"https://t.me/share/url?url=&text={encoded_text}"
    return whatsapp_url, telegram_url

if user_query:
    if not is_valid_query(user_query):
        st.warning("⚠️ Invalid format. Use queries like:\n- Top 10 Sports News Today\n- Top 10 Mumbai Politics News Today")
    else:
        with st.spinner("🔁 Fetching and summarizing live news..."):
            articles = fetch_news(user_query, country_code)

            if not articles:
                st.error("❌ No news found for that topic today.")
            else:
                summary_output = format_summaries(user_query, articles)
                st.markdown("### ✅ Top 10 Real-Time News Summaries")
                st.markdown(summary_output)

                # Share buttons
                st.markdown("---")
                st.subheader("📤 Share This Summary")
                wa_link, tg_link = generate_share_links(summary_output)
                st.markdown(f"[💬 Share on WhatsApp]({wa_link})", unsafe_allow_html=True)
                st.markdown(f"[📢 Share on Telegram]({tg_link})", unsafe_allow_html=True)
