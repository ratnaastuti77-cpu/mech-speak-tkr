import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import json

st.set_page_config(page_title="MECH-SPEAK AI - TKR", page_icon="🔧", layout="centered")

st.title("🔧 MECH-SPEAK AI")
st.subheader("Guided English Speaking Simulator for Automotive (TKR)")

api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
if not api_key:
    api_key = st.sidebar.text_input("Masukkan Gemini API Key:", type="password").strip()

if not api_key:
    st.warning("⚠️ Silakan masukkan Gemini API Key terlebih dahulu.")
    st.stop()

client = genai.Client(api_key=api_key, http_option={'api_version':'v1alpha'}

scenarios = {
    "1. Engine Overheating (Mesin Cepat Panas)": "You are Mr. John, an expatriate customer whose car engine is overheating and releasing white smoke. You are worried and asking the student (Service Advisor) for help.",
    "2. Squeaking Brakes (Rem Berbunyi)": "You are Sarah, a foreign customer complaining that your car brakes make a loud squeaking noise when stopping. Ask the student (Service Advisor) what needs to be checked.",
    "3. Routine Oil Change (Ganti Oli Berkala)": "You are Mr. David, a customer who wants a routine engine oil and filter change. Ask the student (Service Advisor) about the oil type, price, and estimated time."
}

selected_scenario = st.selectbox("Pilih Skenario Bengkel Hari Ini:", list(scenarios.keys()))

if "messages" not in st.session_state or st.session_state.get("current_scenario") != selected_scenario:
    st.session_state.current_scenario = selected_scenario
    st.session_state.messages = []
    st.session_state.guides = [
        {
            "en": "Good morning! Welcome to SMK Automotive Workshop. How can I help you with your car today?",
            "id": "Selamat pagi! Selamat datang di Bengkel Otomotif SMK. Ada yang bisa saya bantu dengan mobil Anda hari ini?"
        }
    ]
    st.session_state.audio_bytes = None
    st.session_state.feedback = None

def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

def get_ai_response(history, scenario_desc):
    prompt = f"""
    Roleplay Context: {scenario_desc}
    The user is a beginner Indonesian vocational high school student (TKR / Automotive) acting as a Service Advisor.
    Keep your response short (1-2 simple sentences) and natural as a customer.
    Also provide 2 simple, polite English response options for the student to read aloud next, along with their Indonesian translations.
    
    Respond ONLY in valid JSON format with this exact structure:
    {{
        "customer_reply": "Your spoken reply as the customer in English",
        "options": [
            {{"en": "First suggested English sentence for student to read", "id": "Arti bahasa Indonesia opsi 1"}},
            {{"en": "Second suggested English sentence for student to read", "id": "Arti bahasa Indonesia opsi 2"}}
        ]
    }}
    """
    contents = [prompt]
    for msg in history:
        contents.append(f"{msg['role']}: {msg['text']}")
        
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

st.markdown("---")
for msg in st.session_state.messages:
    if msg["role"] == "Student":
        st.chat_message("user").write(f"**Kamu (Service Advisor):** {msg['text']}")
    else:
        st.chat_message("assistant").write(f"**Pelanggan (AI):** {msg['text']}")

if st.session_state.audio_bytes:
    st.audio(st.session_state.audio_bytes, format="audio/mp3", autoplay=True)

st.info("📖 **Panduan Teks untuk Dibaca Siswa (Pilih salah satu dan baca dengan lantang):**")
for idx, opt in enumerate(st.session_state.guides, 1):
    st.markdown(f"**Opsi {idx}:** `{opt['en']}`  \n*Artinya: {opt['id']}*")

st.markdown("### 🎙️ Tekan Tombol di Bawah untuk Bicara:")
audio = mic_recorder(
    start_prompt="🔴 Mulai Bicara (Record)",
    stop_prompt="⏹️ Selesai Bicara (Stop)",
    just_once=True,
    format="wav",
    key=f"mic_{len(st.session_state.messages)}"
)

if audio:
    with st.spinner("Mendengarkan dan memproses suara kamu..."):
        try:
            transcribe_resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    "Listen to this audio and transcribe the English speech accurately. Return ONLY the spoken words without any extra explanation.",
                    types.Part.from_bytes(data=audio["bytes"], mime_type="audio/wav")
                ]
            )
            student_text = transcribe_resp.text.strip()
            st.session_state.messages.append({"role": "Student", "text": student_text})
            
            ai_data = get_ai_response(st.session_state.messages, scenarios[selected_scenario])
            customer_text = ai_data["customer_reply"]
            st.session_state.messages.append({"role": "Customer", "text": customer_text})
            st.session_state.guides = ai_data["options"]
            st.session_state.audio_bytes = text_to_speech(customer_text)
            st.rerun()
        except Exception as e:
            st.error(f"Detail Error: {e}")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("📊 Selesai & Lihat Nilai Speaking"):
        if len(st.session_state.messages) < 2:
            st.warning("Lakukan percakapan minimal 1 kali sebelum melihat nilai.")
        else:
            with st.spinner("AI sedang menilai kemampuan speaking kamu..."):
                transcript = "\n".join([f"{m['role']}: {m['text']}" for m in st.session_state.messages])
                eval_prompt = f"""
                Evaluate this beginner Indonesian automotive (TKR) student's speaking practice based on this transcript:
                {transcript}
                
                Provide encouraging feedback in Indonesian with:
                1. Skor Speaking (0-100)
                2. Apresiasi penggunaan istilah otomotif
                3. Koreksi kata/kalimat yang kurang tepat dan cara pengucapan yang benar.
                """
                eval_resp = client.models.generate_content(model="gemini-2.5-flash", contents=eval_prompt)
                st.session_state.feedback = eval_resp.text

with col2:
    if st.button("🔄 Ulangi Simulasi dari Awal"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if st.session_state.feedback:
    st.success("### 🏆 Rapor Penilaian Speaking Otomatis")
    st.write(st.session_state.feedback)
