import streamlit as st
import google.generativeai as genai
import json

# 1. ማዋቀር
st.set_page_config(page_title="AI Pronunciation Coach", page_icon="🎙️")

# ሚስጥራዊ ቁልፍ መቀበል
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API Key አልተገኘም! እባክዎ Streamlit Secrets ላይ ያስገቡ።")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 2. ዲዛይን
st.title("🎙️ እንግሊዝኛን በ AI ይለማመዱ")

# URL Parameters (?word=...&lang=...)
if "query_params" not in st.session_state:
    st.session_state.query_params = st.query_params

default_word = st.query_params.get("word", "Welcome")
user_lang = st.query_params.get("lang", "Amharic")

st.caption(f"የአስተያየት ቋንቋ: **{user_lang}**")
target_text = st.text_input("የሚለማመዱት ቃል:", value=default_word)

audio_value = st.audio_input("ድምጽዎን ይቅረጹ (Record)")

# 3. ዋናው ስራ
if audio_value:
    with st.spinner("እየሰማሁ ነው..."):
        try:
            audio_bytes = audio_value.read()
            
            prompt = f"""
            You are a pronunciation coach.
            Target: "{target_text}"
            User Language: "{user_lang}"
            
            Task:
            1. Transcribe what the user said exactly.
            2. Compare with target.
            3. Give score (0-100).
            4. Give feedback in {user_lang}.
            
            Return JSON:
            {{
                "transcription": "...",
                "score": 0,
                "feedback": "..."
            }}
            """
            
            response = model.generate_content([
                prompt,
                {"mime_type": "audio/wav", "data": audio_bytes}
            ])
            
            text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            
            st.divider()
            st.metric("ውጤት", f"{result['score']}%")
            st.write(f"**የሰማሁት:** {result['transcription']}")
            st.info(result['feedback'])
            
        except Exception as e:

            st.error(f"Error: {e}")
