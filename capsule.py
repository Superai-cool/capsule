import streamlit as st
import openai
from PIL import Image
import base64
import io

# --- OpenAI API Key ---
openai.api_key = st.secrets["openai"]["api_key"]

# --- Page Setup ---
st.set_page_config(page_title="NutriBaby", layout="centered", page_icon="🍼")

# --- Inject Custom Font (Poppins) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🍼 NutriBaby - Baby Food Label Analyzer")
st.markdown("Get accurate, age-based nutritional analysis of baby food labels.")

# --- Age Filter ---
age_group = st.selectbox("Select Your Baby's Age Group:", [
    "0–6 months", "6–12 months", "1–2 years", "2+ years"
])

# --- Upload Instructions ---
with st.expander("📸 How to Upload Food Label", expanded=False):
    st.markdown("""
    - Take a **clear photo** of the baby food label (ingredients + nutrition).
    - Upload it below to get a detailed analysis.
    """)

uploaded_file = st.file_uploader("Upload Label Image", type=["jpg", "jpeg", "png"])

# --- Validate Image ---
def is_image_clear(image: Image.Image) -> bool:
    return image.width >= 300 and image.height >= 300

# --- GPT Analysis Function ---
def analyze_label(image_bytes, age_group):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = f"""
You are NutriBaby, a certified expert in infant and toddler nutrition.

Analyze the uploaded food label and return a detailed, well-formatted report using this structure (DO NOT include the title in the response):

🥣 Quick Overview (Per 100g)
- Calories
- Total Fat (break into Saturated + Trans)
- Carbohydrates
  - Added Sugar
- Protein
- Calcium

**Ingredients Check**

- List ingredients with emojis and remarks (✅ good, ⚠️ moderate, 🚫 avoid)

**Concerns by Age Group**

- 6–12 months
- 1–2 years
- 2+ years

**NutriBaby Tips**

- Suggest healthy alternatives
- Simple feeding tips with emojis

End with:

Powered by SuperAI  
Join NutriBaby Parents <a href="https://chat.whatsapp.com/L3rhA1Pg9jUA6VMwWqbPkC">Whatsapp</a> Community

DO NOT include download/copy/share buttons. Just formatted text.
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

# --- App Logic ---
if uploaded_file:
    image = Image.open(uploaded_file)

    if not is_image_clear(image):
        st.warning("⚠️ Please upload a clearer image with visible nutritional values and ingredients.")
    else:
        st.image(image, caption="Uploaded Label", use_container_width=True)

        if st.button("Analyze Now"):
            with st.spinner("Analyzing with NutriBaby..."):
                image_bytes = io.BytesIO()
                image.save(image_bytes, format="JPEG")

                try:
                    result = analyze_label(image_bytes.getvalue(), age_group)
                except openai.RateLimitError:
                    st.error("⚠️ OpenAI is currently rate-limiting you. Please wait a minute and try again.")
                    st.stop()
                except openai.OpenAIError as e:
                    st.error(f"❌ An error occurred while contacting OpenAI: {e}")
                    st.stop()

            st.markdown("**NutriBaby Food Label Analysis**")

            st.markdown(f"""
<div style="background:#f8f9fa; padding:1rem; border-radius:12px; font-family: 'Poppins', sans-serif;">
{result}
</div>
""", unsafe_allow_html=True)

else:
    # --- Static Demo Output ---
    demo_result = """
## 🥣 Quick Overview *(Per 100g)*  
- **Calories:** 79 kcal  
- **Total Fat:** 2.1 g  
  - Saturated: 1.4 g  
  - Trans: 0.1 g  
- **Carbohydrates:** 12.8 g  
  - **Added Sugar:** 12.0 g 🚨  
- **Protein:** 2.3 g  
- **Calcium:** 74 mg

---

## 🧾 Ingredients Check  
| Ingredient                        | Verdict | Notes |
|----------------------------------|--------|-------|
| 🥛 **Toned Milk Dahi**            | ✅      | Good source of calcium and protein. |
| 💧 **Water**                      | ✅      | Keeps baby hydrated. |
| 🍬 **Sugar**                      | 🚫      | High sugar content; moderation needed. |
| ⚖️ **Permitted Stabilizer (E 440)** | ⚠️      | Generally safe, but excess may affect digestion. |
| 🌹 **Added Flavour (Rose)**       | 🚫      | Avoid artificial additives for infants. |

---

## 👶 Concerns by Age Group  

- **6–12 months:**  
  🚫 *Avoid.* High sugar and artificial flavors are not suitable.

- **1–2 years:**  
  ⚠️ *Limit consumption.* Added sugar and flavors should be minimized.

- **2+ years:**  
  ✅ *Okay occasionally.* Balance with a wholesome diet.

---

## 💡 NutriBaby Tips  
- 🍓 *Go homemade:* Try plain yogurt with mashed or soft fruits.  
- 🌿 *Flavor naturally:* Add mild spices or fruit purees to introduce variety.  

---

## 🤝 Join Our Parent Circle  
💬 **Join the [NutriBaby Parents WhatsApp Community](https://chat.whatsapp.com/L3rhA1Pg9jUA6VMwWqbPkC)** for expert tips, meal plans, and real-parent support!

---

*Powered by SuperAI · Built for Baby Nutrition*
"""
    st.markdown("**NutriBaby Food Label Analysis (Example)**")
    st.markdown(f"""
<div style="background:#f8f9fa; padding:1rem; border-radius:12px; font-family: 'Poppins', sans-serif;">
{demo_result}
</div>
""", unsafe_allow_html=True)
