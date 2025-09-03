# streamlit_app.py
import streamlit as st
import requests

API_URL = "http://localhost:8000/transcribe"

st.set_page_config(page_title="Meeting Notes & Action Items", layout="wide")

st.title("🎙️ Meeting Notes & Action Item Extractor")

# Upload audio file
uploaded_file = st.file_uploader("Upload a meeting audio file", type=["mp3", "wav", "m4a"])

language = st.selectbox("Language", ["auto", "en", "hi", "fr", "de"])
model_name = st.selectbox("Model", ["tiny", "base", "small", "medium", "large"])
use_llm = st.checkbox("Use LLM for extraction", value=True)

if uploaded_file is not None:
    if st.button("Transcribe & Extract"):
        with st.spinner("Processing..."):
            files = {
                "file": (uploaded_file.name, uploaded_file, "audio/mpeg"),
            }
            data = {
                "language": None if language == "auto" else language,
                "diarize": "false",
                "model_name": model_name,
                "use_llm": str(use_llm).lower(),
            }

            response = requests.post(API_URL, files=files, data=data)

            if response.status_code == 200:
                result = response.json()

                st.subheader("📝 Transcript")
                st.write(result["transcript"])

                st.subheader("📌 Summary")
                st.write(result["summary"])

                st.subheader("🔑 Key Points")
                for kp in result["key_points"]:
                    st.markdown(f"- {kp}")

                st.subheader("✅ Action Items")
                if result["action_items"]:
                    for ai in result["action_items"]:
                        st.markdown(
                            f"- **Task**: {ai['task']} "
                            f"{'(Assignee: ' + ai['assignee'] + ')' if ai['assignee'] else ''} "
                            f"{'(Due: ' + ai['due'] + ')' if ai['due'] else ''}"
                        )
                        if ai.get("context"):
                            st.caption(ai["context"])
                else:
                    st.write("No action items found.")

                st.subheader("⏱️ Segments")
                for seg in result.get("segments", []):
                    st.markdown(f"[{seg['start']}s → {seg['end']}s] {seg['text']}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
