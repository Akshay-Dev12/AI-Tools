import streamlit as st
import requests
from pdf_utils import extract_text_from_pdf

# Page configuration
st.set_page_config(
    page_title="Gama Document Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_summary(text: str, length: str):
    """
    Sends text to the backend API and returns the summary and keywords.
    """
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/summarize",
            json={"text": text, "summary_length": length.lower()},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("summary", ""), data.get("keywords", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {e}")
        return None, []


def main():
    """
    Main function to render the Streamlit UI.
    """
    # Custom CSS for styling
    st.markdown(
        """
        <style>
            .stTextArea [data-baseweb="base-input"] {
                border-radius: 10px;
                border-width: 2px;
            }
            .stButton>button {
                border-radius: 10px;
                border: 2px solid #4F8BF9;
                color: #4F8BF9;
            }
            .stButton>button:hover {
                border: 2px solid #4F8BF9;
                color: white;
                background-color: #4F8BF9;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.title("📄 Gama Summarizer")
        st.subheader("Upload your document")
        uploaded_file = st.file_uploader(
            "Upload a PDF file", type="pdf", label_visibility="collapsed"
        )

        st.subheader("Summary Options")
        summary_length = st.radio(
            "Select Summary Length",
            ("Short", "Medium", "Long"),
            index=1,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.info("Powered by Seqato")

    # Main content
    st.header("Document Summarization Tool")

    if uploaded_file:
        with st.spinner("Extracting text from your document..."):
            extracted_text = extract_text_from_pdf(uploaded_file)

        with st.expander("View Extracted Text"):
            st.text_area("Extracted Text", extracted_text, height=250)

        if st.button("✨ Summarize Document"):
            with st.spinner("Generating summary... Please wait."):
                summary, keywords = get_summary(extracted_text, summary_length)
                if summary:
                    st.subheader("📝 Summary")
                    st.success(summary)

                    st.subheader("🔑 Keywords")
                    st.write(", ".join(f"`{kw}`" for kw in keywords))

                    st.download_button(
                        label="📥 Download Summary",
                        data=summary,
                        file_name="summary.txt",
                        mime="text/plain",
                    )
                else:
                    st.error("Could not generate summary.")
    else:
        st.info("Please upload a PDF document to get started.")


if __name__ == "__main__":
    main()