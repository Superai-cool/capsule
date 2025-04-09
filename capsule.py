import streamlit as st
import openai
import requests
import re
import random
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

valid_query_pattern = re.compile(
    r"^Top 10 ([A-Za-z]+|[A-Za-z]+\s[A-Za-z]+) (News Today|[A-Za-z]+\sNews Today)$"
)

# UI
st.set_page_config(page_title="Capsule – Live News", layout="centered")
st.title("📰 Capsule – Live News Summarizer")

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

def fetch_news_from_api(query):
    topic = extract_topic(query)
    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=publishedAt&pageSize=15&apiKey={NEWS_API_KEY}"
    res = requests.get(url)
    articles = res.json().get("articles", [])
    return [
        {
            "title": article["title"],
            "description": article["description"],
            "source": article["source"]["name"],
            "url": article["url"]
        }
        for article in articles if article["title"]
    ]

def summarize_with_gpt(query, articles):
    today = datetime.now().strftime("%B %d, %Y")
    sponsor_text = "\n".join(random.sample(sponsor_lines, 10))
    
    news_text = "\n".join(
        [f"- {a['title']} ({a['source']})" for a in articles[:10]]
    )

    prompt = f"""
You are Capsule – an English-only news summarizer for India.

Query: "{query}"  
Date: {today}

🎯 Summarize these 10 real articles into properly formatted summaries:

{news_text}

📦 Format each like this:

<number>. {query} | {today}  
**Headline**  
Summary (60–70 words)  
📣 [One sponsor line from below]  
---

Sponsors (use each once, any order):
{sponsor_text}

✅ End with:  
✅ All 10 news checked—done for today! 🎯

Do NOT fabricate news. Do NOT mix topics. Do NOT use markdown links.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content.strip()

if user_query:
    if not is_valid_query(user_query):
        st.warning("⚠️ Invalid format. Use queries like:\n- Top 10 Sports News Today\n- Top 10 Mumbai Politics News Today")
    else:
        with st.spinner("🧠 Fetching live headlines + generating summaries..."):
            news_articles = fetch_news_from_api(user_query)

            if not news_articles:
                st.error("❌ No live articles found for this topic today.")
            else:
                final_output = summarize_with_gpt(user_query, news_articles)
                st.markdown("### ✅ Top 10 Real-Time News Summaries")
                st.markdown(final_output)
