import streamlit as st
import requests
from pdf_utils import extract_text_from_pdf

st.title("📄 Gama Document Summarizer")
st.subheader("Powered By Seqato")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extracting text..."):
        text = extract_text_from_pdf(uploaded_file)
        st.text_area("Extracted Text", text, height=300)

    if st.button("Summarize"):
        with st.spinner("Summarizing..."):
            response = requests.post(
                "http://localhost:8000/api/v1/summarize",
                json={"text": text}
            )
            if response.status_code == 200:
                summary = response.json().get("summary", "")
                st.text_area("Summary", summary, height=200)
            else:
                st.error("Failed to get summary from backend.")
