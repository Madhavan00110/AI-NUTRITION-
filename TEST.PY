import os
import json
import streamlit as st
from gtts import gTTS
import plotly.express as px
import google.generativeai as genai

# Set up Gemini API
genai.configure(api_key="AIzaSyCpQlEb0SA47-ikwi-8jSxGtDwlgXoClMs")  # Replace with your key

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "nutrition_json" not in st.session_state:
    st.session_state.nutrition_json = None

if "editable_plan" not in st.session_state:
    st.session_state.editable_plan = ""

if "grocery_list" not in st.session_state:
    st.session_state.grocery_list = ""

if "plan_audio_path" not in st.session_state:
    st.session_state.plan_audio_path = None

# Helper to extract JSON from plan text
def extract_json(text):
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except:
        return None

# Generate chat response
def generate_chat_response():
    user_input = st.session_state.user_input
    language = st.session_state.language
    if user_input:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Respond in {language}.\n\n{user_input}"
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            st.session_state.history.append({"query": user_input, "response": response_text})
            lang_code = 'ta' if language == "Tamil" else 'en'
            tts = gTTS(text=response_text, lang=lang_code)
            tts.save("response.mp3")
            st.session_state.user_input = ""
        except Exception as e:
            st.error(f"Error: {e}")

# Generate plan and audio
def generate_nutrition_plan(user_info):
    language = st.session_state.language
    lang_code = 'ta' if language == "Tamil" else 'en'
    
    prompt = f"""
You are a professional nutrition advisor. Create a detailed, personalized plan based on the user's info below. Respond in {language}.

User Info:
Age: {user_info['age']}
Gender: {user_info['gender']}
Height: {user_info['height']}
Weight: {user_info['weight']}
Activity Level: {user_info['activity_level']}
Goals: {user_info['goals']}
Medical Conditions: {user_info['medical_conditions']}
Medications: {user_info['medications']}
Allergies: {user_info['allergies']}
Food Preferences: {user_info['food_preferences']}
Cooking Ability: {user_info['cooking_ability']}
Budget: {user_info['budget']}
Cultural Factors: {user_info['cultural_factors']}

Provide:
1. A human-readable nutrition plan.
2. A JSON summary like:
{{
  "daily_calories": 2200,
  "macros": {{"protein": 150, "carbs": 200, "fats": 70}},
  "meals": {{
    "breakfast": {{
      "items": ["Oats", "Banana", "Almond Milk"],
      "calories": 400,
      "protein": 15
    }}
  }}
}}
3. A grocery list of required items.
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        full_text = response.text.strip()
        st.session_state.editable_plan = full_text
        st.session_state.nutrition_json = extract_json(full_text)

        if st.session_state.nutrition_json:
            end_json = full_text.rfind("}") + 1
            st.session_state.grocery_list = full_text[end_json:].strip()

        # Generate full plan audio
        tts = gTTS(text=full_text, lang=lang_code)
        audio_path = f"plan_audio_{lang_code}.mp3"
        tts.save(audio_path)
        st.session_state.plan_audio_path = audio_path

        return full_text
    except Exception as e:
        st.error(f"Error generating plan: {e}")
        return None

# UI Setup
st.set_page_config(page_title="Gemini AI + Nutrition", layout="wide")

st.markdown("""
<style>
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        background-color: #f0f0f0;
        border-radius: 8px;
    }
    .ai-name {
        font-size: 26px;
        font-weight: bold;
        color: #4B9CD3;
        margin-bottom: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ai-name">Nutrition Assistant</div>', unsafe_allow_html=True)

# Language selector
st.sidebar.selectbox("Select Language", ["English", "Tamil"], key="language")

# Tabs
tab1, tab2 = st.tabs(["💬 Chat", "🥗 Nutrition Advisor"])

# Chat tab
with tab1:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for item in st.session_state.history:
        st.write(f"**You:** {item['query']}")
        st.write(f"**AI:** {item['response']}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.text_input("Ask something...", key="user_input", on_change=generate_chat_response, label_visibility="collapsed")

    if st.session_state.history:
        st.audio("response.mp3", format="audio/mp3")

# Nutrition tab
with tab2:
    st.header("Tell us about yourself")

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 1, 120, 30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.text_input("Height", "5'10\"")
        activity_level = st.select_slider("Activity", ["Sedentary", "Light", "Moderate", "Very", "Extreme"])
    with col2:
        weight = st.text_input("Weight", "160 lbs")
        goals = st.multiselect("Goals", ["Weight Loss", "Muscle Gain", "Energy", "Health", "Performance"])

    st.subheader("Health & Preferences")
    medical_conditions = st.text_area("Medical Conditions")
    medications = st.text_area("Medications")
    allergies = st.text_area("Allergies")
    food_preferences = st.text_area("Food Preferences")
    cooking_ability = st.select_slider("Cooking Skill", ["Very Limited", "Basic", "Average", "Advanced"])
    budget = st.select_slider("Budget", ["Low", "Medium", "High"])
    cultural_factors = st.text_area("Cultural Factors")

    user_info = {
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "activity_level": activity_level,
        "goals": ", ".join(goals),
        "medical_conditions": medical_conditions,
        "medications": medications,
        "allergies": allergies,
        "food_preferences": food_preferences,
        "cooking_ability": cooking_ability,
        "budget": budget,
        "cultural_factors": cultural_factors
    }

    if st.button("Generate Nutrition Plan"):
        if not goals:
            st.error("Please select at least one goal.")
        else:
            with st.spinner("Generating plan..."):
                result = generate_nutrition_plan(user_info)
            if result:
                st.success("Here is your personalized nutrition plan:")
                st.text_area("Editable Plan", value=st.session_state.editable_plan, height=300, key="editable_plan_area")
                
                st.download_button("📥 Download Meal Plan (Text)", result, "nutrition_plan.txt", mime="text/plain")

                if st.session_state.nutrition_json:
                    st.download_button("📥 Download Meal Plan (JSON)", json.dumps(st.session_state.nutrition_json, indent=2), "nutrition_data.json", mime="application/json")

                    macros = st.session_state.nutrition_json.get("macros", {})
                    if macros:
                        fig = px.pie(names=list(macros.keys()), values=list(macros.values()), title="Macronutrient Distribution")
                        st.plotly_chart(fig)

                if st.session_state.grocery_list:
                    st.subheader("🛒 Grocery List")
                    st.text(st.session_state.grocery_list)

                if st.session_state.plan_audio_path:
                    st.subheader("🔊 Listen to Full Plan")
                    st.audio(st.session_state.plan_audio_path, format="audio/mp3")