import streamlit as st
# Title
st.title("Hello, Streamlit!")

# Header
st.header("This is a header")

# Subheader
st.subheader("This is a subheader")

# Text
st.text("Welcome to Streamlit app tutorial")

# Markdown
st.markdown("**Bold Text** and _Italic Text_")

# Button
if st.button("Click me"):
    st.write("Button clicked!")

# Text input
name = st.text_input("Enter your name")
if name:
    st.write(f"Hello, {name}!")

# Slider
age = st.slider("Select your age", 0, 100, 25)
st.write("Your age is", age)

# Checkbox
if st.checkbox("Show image"):
    st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png", width=250)

# Selectbox
language = st.selectbox("Pick a language", ["Python", "Java", "C++"])
st.write("You selected:", language)

# Data display
import pandas as pd
df = pd.DataFrame({
    "Name": ["Akshay", "John", "Sara"],
    "Age": [25, 30, 22]
})
st.dataframe(df)

col1, col2 = st.columns(2)

with col1:
    st.write("Left column")
    st.subheader("Hai")
    st.text("Left column area")

with col2:
    st.write("Right column")
    st.subheader("Hai")
    st.text("Right column area")