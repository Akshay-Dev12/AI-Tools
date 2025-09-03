import streamlit as st
import requests

# API endpoint
API_URL = "http://localhost:8000/chat"

st.title("📸 LLaVA Image Chat")
st.write("Ask questions about an image using LLaVA.")

# User inputs
prompt = st.text_input("Enter your prompt:", "Give me details about this photo.?")
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if st.button("Ask"):
    if uploaded_file and prompt:
        # Prepare multipart form data
        files = {
            "image": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }
        data = {
            "prompt": prompt
        }

        with st.spinner("🔍 Analyzing image..."):
            response = requests.post(API_URL, files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            st.subheader("Response:")
            st.write(result.get("response", "No response"))
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("Please upload an image and enter a prompt.")