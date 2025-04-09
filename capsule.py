import streamlit as st
import openai
from PIL import Image
import base64
import io

# Set OpenAI API Key from secrets
openai.api_key = st.secrets["openai"]["api_key"]

# --- Branding Strings ---
BRANDING_START = "**Powered by SuperAI**"
BRANDING_END = "**Join NutriBaby Parents Community** – [click here](https://chat.whatsapp.com/L3rhA1Pg9jUA6VMwWqbPkC)."

# --- Page Config ---
st.set_page_config(
    page_title="NutriBaby - Baby Food Analyzer",
    layout="centered",
    page_icon="🍼",
)

# --- Custom Styles ---
st.markdown("""
    <style>
    .main { background-color: #F9FAFC; }
    button {
        background-color: #5A9;
        color: white;
        padding: 8px 20px;
        border-radius: 12px;
        font-weight: bold;
        margin-top: 10px;
    }
    .uploadedImage {
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title Section ---
st.markdown("## 🍼 Welcome to **NutriBaby**")
st.markdown("Helping parents make smarter food choices for their babies and toddlers.")

# --- Step Guide ---
with st.expander("📋 How to Analyze Baby Food Labels (Tap to expand)", expanded=False):
    st.markdown("""
    1️⃣ **Take a clear photo** of the food label showing both **nutritional values** and **ingredients**.  
    2️⃣ **Upload the image** below for instant analysis.
    """)

# --- Upload Image ---
st.markdown("### 📤 Upload Food Label Image")
uploaded_file = st.file_uploader("Only baby/toddler food labels are accepted (ingredients + nutrition).", type=["png", "jpg", "jpeg"])

def is_image_clear(image: Image.Image) -> bool:
    # Simple resolution check
    min_width, min_height = 300, 300
    return image.width >= min_width and image.height >= min_height

def analyze_label(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": (
                "You are NutriBaby, an expert nutrition assistant for baby and toddler food. "
                "Analyze food label images provided by users and give detailed, scientifically accurate advice. "
                "Focus on nutrients, allergens, sugars, and additives. Provide clear, age-appropriate guidance, and suggest better alternatives if needed. "
                "Always start with 'Powered by SuperAI' and end with 'Join NutriBaby Parents Community – [click here](https://chat.whatsapp.com/L3rhA1Pg9jUA6VMwWqbPkC).' "
                "Respond only to food-related labels. Politely reject unclear, blurry, or unrelated images."
            )},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()

# --- Analyze Button ---
if uploaded_file:
    image = Image.open(uploaded_file)

    if not is_image_clear(image):
        st.warning("Image is too blurry or small. Please upload a clearer photo showing full nutritional info.")
    else:
        st.image(image, caption="Uploaded Label", use_column_width=True, output_format="JPEG")

        if st.button("🔍 Analyze Now"):
            with st.spinner("Analyzing label..."):
                image_bytes = io.BytesIO()
                image.save(image_bytes, format="JPEG")
                analysis = analyze_label(image_bytes.getvalue())

            # Display Result
            st.markdown(f"{BRANDING_START}\n\n{analysis}\n\n{BRANDING_END}")

else:
    st.info("Upload a baby food label image to begin.")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ to support healthy baby nutrition.")
