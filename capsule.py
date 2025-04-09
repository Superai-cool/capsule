import streamlit as st
import openai
from PIL import Image
import base64
import io

# --- OpenAI Key ---
openai.api_key = st.secrets["openai"]["api_key"]

# --- Branding Texts ---
BRANDING_START = "**Powered by SuperAI**"
BRANDING_END = "**Join NutriBaby Parents Community** – [click here](https://chat.whatsapp.com/L3rhA1Pg9jUA6VMwWqbPkC)"

# --- Page Setup ---
st.set_page_config(page_title="NutriBaby", layout="centered", page_icon="🍼")

# --- Styles ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #FF6B6B;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.5em 1em;
    }
    .stDownloadButton>button {
        background-color: #1E90FF;
        color: white;
        border-radius: 6px;
        margin-top: 10px;
    }
    .container-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("🍼 NutriBaby - Baby Food Label Analyzer")
st.markdown("Analyze food labels for infants and toddlers. Get science-backed, age-appropriate advice.")

# --- Age Filter ---
age_group = st.selectbox("👶 Select Your Baby's Age Group:", [
    "0–6 months", "6–12 months", "1–2 years", "2+ years"
])

# --- Upload Section ---
with st.expander("📸 How to Upload Food Label", expanded=False):
    st.markdown("1️⃣ Take a **clear photo** of the food label (nutritional values + ingredients).  \n"
                "2️⃣ Upload it below. NutriBaby will analyze and explain everything.")

uploaded_file = st.file_uploader("📤 Upload Baby Food Label", type=["png", "jpg", "jpeg"])

# --- Check if image is clear ---
def is_image_clear(image: Image.Image) -> bool:
    return image.width >= 300 and image.height >= 300

# --- Analyze Image via GPT ---
def analyze_label(image_bytes, age_group):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        f"You are NutriBaby, a certified nutrition expert for babies and toddlers. "
        f"The user has selected age group: **{age_group}**.\n\n"
        "Analyze the uploaded food label image and provide:\n"
        "- Nutritional overview with emojis per 100g\n"
        "- Highlight any health concerns for the selected age\n"
        "- Suggest better alternatives if necessary\n"
        "- Recommend how or when to feed\n\n"
        "Always format your reply like this:\n"
        "1. 🔋 Nutritional Breakdown (with emojis)\n"
        "2. 🧾 Ingredients (if readable)\n"
        "3. ⚠️ Nutritional Concerns (highlight sugars, additives, etc.)\n"
        "4. ✅ NutriBaby Recommends (better alternatives or tips)\n"
        "5. End with branding:\n"
        "Powered by SuperAI\n"
        "Join NutriBaby Parents Community – click here"
    )

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
        max_tokens=1200
    )
    return response.choices[0].message.content.strip()

# --- Clipboard Copy Button ---
def clipboard_button(text):
    st.markdown(f"""
    <textarea id="copyTarget" style="opacity:0; height:1px;">{text}</textarea>
    <button onclick="navigator.clipboard.writeText(document.getElementById('copyTarget').value)"
            style="margin-top:10px;background-color:#48c78e;color:white;padding:8px 16px;border:none;border-radius:6px;">
        📋 Copy to Clipboard
    </button>
    """, unsafe_allow_html=True)

# --- Main Logic ---
if uploaded_file:
    image = Image.open(uploaded_file)

    if not is_image_clear(image):
        st.warning("⚠️ Image is too small or blurry. Please upload a clearer photo showing full nutritional info.")
    else:
        st.image(image, caption="📸 Uploaded Label", use_container_width=True, output_format="JPEG")

        if st.button("🔍 Analyze Now"):
            with st.spinner("Analyzing label with NutriBaby..."):
                image_bytes = io.BytesIO()
                image.save(image_bytes, format="JPEG")
                result = analyze_label(image_bytes.getvalue(), age_group)

            # --- Output Display Box ---
            with st.container():
                st.markdown(f"""<div class="container-box">{result}</div>""", unsafe_allow_html=True)

            # --- Download & Clipboard ---
            st.download_button("📄 Download Report", result, file_name="nutribaby_analysis.txt")
            clipboard_button(result)

else:
    st.info("Upload a food label image to begin.")

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ by SuperAI. For any food concerns, always consult a certified pediatrician.")
