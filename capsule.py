import streamlit as st
import openai
import re
import random
from datetime import datetime

openai.api_key = st.secrets["OPENAI_API_KEY"]

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

st.set_page_config(page_title="Capsule – Top 10 News Summarizer", layout="centered")
st.title("📰 Capsule – Top 10 News Summarizer")

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

def build_prompt(query):
    today = datetime.now().strftime("%B %d, %Y")
    shuffled_sponsors = random.sample(sponsor_lines, 10)
    sponsor_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(shuffled_sponsors)])
    return f"""
You're Capsule – an English-only news summarizer for India.

Query: "{query}"  
Date: {today}

🎯 Task: Write 10 professionally written news summaries (~60–70 words each) ONLY about this topic. Use trusted Indian sources (TOI, Hindu, IE, etc).

📦 Format (repeat exactly 10 times):

<number>. {query} | {today}  
**Headline**  
Summary  
📣 [One sponsor line from the list below]  
---

Sponsors (use one per item, any order):
{sponsor_text}

✅ End with:  
✅ All 10 news checked—done for today! 🎯

❌ Do NOT use markdown-style links like [text](url).  
❌ Do NOT include multiple sources, emojis, commentary, or non-English.
"""

if user_query:
    if not is_valid_query(user_query):
        st.warning("""
        📢 **Capsule** works only with **properly formatted requests.**

        ✅ Try formats like:  
        - Top 10 Sports News Today  
        - Top 10 Mumbai News Today  
        - Top 10 Delhi Politics News Today
        """)
    else:
        with st.spinner("Generating your top 10 news..."):
            prompt = build_prompt(user_query)
            attempts = 0
            response_valid = False

            while attempts < 2 and not response_valid:
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=2000
                    )
                    result = response.choices[0].message.content.strip()

                    # Validate counts
                    divider_count = result.count('---')
                    heading_count = len(re.findall(r'\*\*(.*?)\*\*', result))
                    sponsor_count = len(re.findall(r'📣', result))

                    if divider_count == 10 and heading_count == 10 and sponsor_count == 10:
                        response_valid = True
                        st.markdown("### ✅ Top 10 News Summaries")
                        st.markdown(result)
                    elif divider_count >= 8 and heading_count >= 8 and sponsor_count >= 8:
                        response_valid = True
                        st.warning("⚠️ Response slightly misformatted but displayed anyway:")
                        st.markdown(result)
                    else:
                        attempts += 1

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    break

            if not response_valid:
                st.error("⚠️ Unable to generate a valid response after multiple attempts. Please try again later.")
