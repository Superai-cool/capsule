import streamlit as st
import openai
from PIL import Image
import base64
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tempfile
import urllib.parse

# --- Set OpenAI API Key ---
openai.api_key = st.secrets["openai"]["api_key"]

# --- Branding ---
BRANDING_START = "**Powered by SuperAI**"
BRANDING_END = "**Join NutriBaby Parents Community** – [click here](https://chat.whatsapp.com/L3rhA1Pg9jUA6VMwWqbPkC)"

# --- Page Config ---
st.set_page_config(page_title="NutriBaby", layout="centered", page_icon="🍼")

# --- Custom CSS ---
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

# --- Title ---
st.title("🍼 NutriBaby - Baby Food Label Analyzer")
st.markdown("Analyze food labels for infants and toddlers. Get science-backed, age-appropriate advice.")

# --- Age Filter ---
age_group = st.selectbox("👶 Select Your Baby's Age Group:", [
    "0–6 months", "6–12 months", "1–2 years", "2+ years"
])

# --- Upload Instructions ---
with st.expander("📸 How to Upload Food Label", expanded=False):
    st.markdown("1️⃣ Take a **clear photo** of the food label (nutritional values + ingredients).  \n"
                "2️⃣ Upload it below. NutriBaby will analyze and explain everything.")

uploaded_file = st.file_uploader("📤 Upload Baby Food Label", type=["png", "jpg", "jpeg"])

# --- Check if image is clear ---
def is_image_clear(image: Image.Image) -> bool:
    return image.width >= 300 and image.height >= 300

# --- GPT-4o Analysis Function ---
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

# --- Generate PDF Function ---
def generate_pdf(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        c = canvas.Canvas(tmp_file.name, pagesize=A4)
        width, height = A4
        text_object = c.beginText(40, height - 50)
        text_object.setFont("Helvetica", 11)
        for line in text.split("\n"):
            text_object.textLine(line)
        c.drawText(text_object)
        c.showPage()
        c.save()
        return tmp_file.name

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

            # --- Output Box ---
            with st.container():
                st.markdown(f"""<div class="container-box">{result}</div>""", unsafe_allow_html=True)

            # --- PDF Download ---
            pdf_file_path = generate_pdf(result)
            with open(pdf_file_path, "rb") as f:
                st.download_button("📥 Download as PDF", f, file_name="nutribaby_analysis.pdf", mime="application/pdf")

            # --- WhatsApp Share ---
            encoded_text = urllib.parse.quote(result)
            whatsapp_link = f"https://wa.me/?text={encoded_text}"
            st.markdown(f"""
            <a href="{whatsapp_link}" target="_blank">
                <button style="background-color:#25D366; color:white; padding:10px 18px; border:none; border-radius:6px; font-weight:bold;">
                📤 Share on WhatsApp
                </button>
            </a>
            """, unsafe_allow_html=True)

            # --- Manual Copy ---
            st.text_area("📋 Copy this analysis manually:", value=result, height=200)

else:
    st.info("Upload a food label image to begin.")

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ by SuperAI. For any food concerns, always consult a certified pediatrician.")
