import streamlit as st
import openai
import requests
import re
import random
import urllib.parse
from datetime import datetime

# Load API keys
openai.api_key = st.secrets["OPENAI_API_KEY"]
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

# Sponsors
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

# Valid query formats
valid_query_pattern = re.compile(
    r"^Top 10 ([A-Za-z]+|[A-Za-z]+\s[A-Za-z]+) (News Today|[A-Za-z]+\sNews Today)$"
)

# UI
st.set_page_config(page_title="Capsule – India News", layout="centered")
st.title("🇮🇳 Capsule – Real-Time Indian News Summarizer")

with st.expander("📌 Accepted Formats"):
    st.markdown("""
    1. Top 10 **[Topic]** News Today  
       _Example: Top 10 Sports News Today_  
    2. Top 10 **[City Name]** News Today  
       _Example: Top 10 Delhi News Today_  
    3. Top 10 **[City Name] [Topic]** News Today  
       _Example: Top 10 Mumbai Crime News Today_
    """)

user_query = st.text_input("🔍 Enter your query (must match format)")

def is_valid_query(query):
    return bool(valid_query_pattern.match(query)) and all(ord(c) < 128 for c in query)

def extract_topic(query):
    return query.replace("Top 10", "").replace("News Today", "").strip()

def fetch_indian_news(query):
    topic = extract_topic(query)
    url = f"https://newsapi.org/v2/top-headlines?q={topic}&country=in&language=en&pageSize=10&apiKey={NEWS_API_KEY}"
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
        heading = a['title']
        summary = a['description']
        read_more = f"[🔗 Read more – {a['source']}]({a['url']})"

        formatted = f"""
{idx}. {query} | {today}  
**{heading}**  
{summary}  
{read_more}  
{str(sponsor)}  
---
"""
        summaries.append(formatted.strip())

    summaries.append("✅ All 10 news checked—done for today! 🎯")
    return "\n\n".join(summaries)

def generate_share_links(summary_text):
    share_text = urllib.parse.quote(summary_text[:1500])
    wa_link = f"https://api.whatsapp.com/send?text={share_text}"
    tg_link = f"https://t.me/share/url?url=&text={share_text}"
    return wa_link, tg_link

if user_query:
    if not is_valid_query(user_query):
        st.warning("⚠️ Invalid format. Use:\n- Top 10 Sports News Today\n- Top 10 Delhi News Today\n- Top 10 Mumbai Crime News Today")
    else:
        with st.spinner("🧠 Fetching live headlines from India..."):
            articles = fetch_indian_news(user_query)

            if not articles:
                st.error("❌ No Indian news found for that topic today.")
            else:
                summary_output = format_summaries(user_query, articles)
                st.markdown("### ✅ Today's Indian News")
                st.markdown(summary_output)

                # Share buttons
                st.markdown("---")
                st.subheader("📤 Share This")
                wa_link, tg_link = generate_share_links(summary_output)
                st.markdown(f"[💬 Share on WhatsApp]({wa_link})", unsafe_allow_html=True)
                st.markdown(f"[📢 Share on Telegram]({tg_link})", unsafe_allow_html=True)
