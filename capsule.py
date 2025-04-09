import streamlit as st
import openai
import re
import random
from datetime import datetime

# Load API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Constants
sponsor_lines = [
    "📣 Capsule Ads | Increase Your Business Visibility | [WhatsApp Now](https://wa.link/mwb2hf)",
    "📣 Amazon | One-Stop Online Shopping | [https://www.amazon.com](https://www.amazon.com)",
    "📣 Flipkart | Fashion, Electronics & More | [https://www.flipkart.com](https://www.flipkart.com)",
    "📣 Myntra | Trendy Fashion & Accessories | [https://www.myntra.com](https://www.myntra.com)",
    "📣 Blinkit | Instant Grocery & Essentials | [https://www.blinkit.com](https://www.blinkit.com)",
    "📣 Sid's Farm | Pure & Fresh Dairy Products | [https://www.sidsfarm.com](https://www.sidsfarm.com)",
    "📣 Nykaa | Beauty, Skincare & Cosmetics | [https://www.nykaa.com](https://www.nykaa.com)",
    "📣 Urban Company | Home & Personal Services | [https://www.urbancompany.com](https://www.urbancompany.com)",
    "📣 Zomato | Online Food Delivery & Restaurants | [https://www.zomato.com](https://www.zomato.com)",
    "📣 Porter | Mini Truck & Bike Logistics | [https://www.porter.in](https://www.porter.in)"
]

valid_query_pattern = re.compile(
    r"^Top 10 ([A-Za-z]+|[A-Za-z]+\s[A-Za-z]+) (News Today|[A-Za-z]+\sNews Today)$"
)

# Streamlit UI
st.set_page_config(page_title="Capsule – Top 10 News Summarizer", layout="centered")
st.title("📰 Capsule – Top 10 News Summarizer")
st.markdown("Enter your request in one of the **accepted formats**:")

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

    prompt = f"""
You are Capsule, a strict English-language Indian news summarizer. Only accept queries in this format:

1. Top 10 [Topic] News Today
2. Top 10 [City Name] News Today
3. Top 10 [City Name] [Topic] News Today

Query: "{query}"  
Date: {today}  

Strict Output Rules:
- ✅ Exactly 10 summaries.
- ✅ Each summary must be about the requested category only.
- ✅ Each summary must follow **this exact format**:

<number>. [Topic/City] | {today}  
**Headline**  
Summary (60–70 words only, no bold or quotes)  
📣 [One of the sponsor lines below]  
---

- ❌ No extra content or commentary.
- ❌ Do NOT return less than or more than 10.
- ❌ Do NOT include multiple sources, emojis, or HTML.

Use only today's verified Indian sources: TOI, IE, Mint, Hindu, HT, etc.

Use these 10 sponsors (random order, once each):
{sponsor_text}

End with:  
✅ All 10 news checked—done for today! 🎯
"""
    return prompt, shuffled_sponsors

if user_query:
    if not is_valid_query(user_query):
        st.warning("""
        📢 **Capsule** works only with **properly formatted requests.** Ask in one of the **formats below:**

        📌 Accepted Request Formats:

        1. Top 10 [Topic] News Today  
        Example: Top 10 Sports News Today

        2. Top 10 [City Name] News Today  
        Example: Top 10 Delhi News Today

        3. Top 10 [City Name] [Topic] News Today  
        Example: Top 10 Mumbai Politics News Today

        📩 Need Help?  
        [WhatsApp](https://wa.link/mwb2hf) us your query at +91 8830720742
        """)
    else:
        with st.spinner("Generating your top 10 news..."):
            prompt, shuffled_sponsors = build_prompt(user_query)

            attempts = 0
            response_valid = False
            while attempts < 3 and not response_valid:
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                    )
                    result = response.choices[0].message.content.strip()

                    # Check for 10 summaries and sponsor lines
                    news_items = result.split('---')
                    headings = re.findall(r'\*\*(.*?)\*\*', result)
                    sponsors = [line for line in result.splitlines() if '📣' in line]

                    if len(news_items) == 10 and len(headings) == 10 and len(sponsors) == 10:
                        response_valid = True
                        st.markdown(result)
                    else:
                        attempts += 1
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    break

            if not response_valid:
                st.error("⚠️ Unable to generate a valid response after multiple attempts. Please try again later.")
