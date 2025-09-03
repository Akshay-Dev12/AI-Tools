import streamlit as st
import requests
import logging
import json
from typing import Generator
import time
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger("Streamlit")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

BACKEND_URL = "http://localhost:8005"

# Page config
st.set_page_config(
    page_title="Gamma Global News Topic Tracker",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .summary-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-top: 1rem;
    }
    .headline-item {
        padding: 0.5rem;
        border-bottom: 1px solid #e6e6e6;
    }
    .streaming-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #ff4b4b;
        animation: pulse 1.5s infinite;
        margin-right: 8px;
    }
    .country-flag {
        font-size: 1.2em;
        margin-right: 8px;
    }
    .country-badge {
        background-color: #e6f7ff;
        padding: 4px 8px;
        border-radius: 12px;
        border: 1px solid #91d5ff;
        font-size: 0.9em;
    }
    .language-badge {
        background-color: #fff0f6;
        padding: 4px 8px;
        border-radius: 12px;
        border: 1px solid #ffadd2;
        font-size: 0.9em;
        margin-left: 8px;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Country flag mapping
COUNTRY_FLAGS = {
    "us": "🇺🇸",
    "gb": "🇬🇧",
    "ca": "🇨🇦",
    "au": "🇦🇺",
    "in": "🇮🇳",
    "de": "🇩🇪",
    "fr": "🇫🇷",
    "jp": "🇯🇵",
    "br": "🇧🇷",
    "cn": "🇨🇳",
    "ru": "🇷🇺",
    "mx": "🇲🇽",
    "za": "🇿🇦",
    "ng": "🇳🇬",
    "eg": "🇪🇬",
    "sa": "🇸🇦",
    "ae": "🇦🇪",
    "kr": "🇰🇷",
    "sg": "🇸🇬",
    "id": "🇮🇩",
    "my": "🇲🇾",
    "th": "🇹🇭",
    "vn": "🇻🇳",
    "ph": "🇵🇭",
    "it": "🇮🇹",
    "es": "🇪🇸",
    "nl": "🇳🇱",
    "se": "🇸🇪",
    "no": "🇳🇴",
    "ch": "🇨🇭",
    "tr": "🇹🇷",
    "il": "🇮🇱",
    "pk": "🇵🇰",
    "bd": "🇧🇩",
    "ar": "🇦🇷",
    "cl": "🇨🇱",
    "co": "🇨🇴",
    "pe": "🇵🇪",
    "nz": "🇳🇿"
}

# Language flag mapping
LANGUAGE_FLAGS = {
    "en": "🇺🇸",
    "es": "🇪🇸",
    "fr": "🇫🇷",
    "de": "🇩🇪",
    "it": "🇮🇹",
    "pt": "🇵🇹",
    "ru": "🇷🇺",
    "zh": "🇨🇳",
    "ja": "🇯🇵",
    "ko": "🇰🇷",
    "ar": "🇸🇦",
    "hi": "🇮🇳",
    "ml": "🇮🇳"  # Malayalam (using India flag)
}

# Initialize session state
if 'headlines' not in st.session_state:
    st.session_state.headlines = []
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = "us"
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "en"
if 'available_countries' not in st.session_state:
    st.session_state.available_countries = {}
if 'available_languages' not in st.session_state:
    st.session_state.available_languages = {}
if 'stop_streaming' not in st.session_state:
    st.session_state.stop_streaming = False
if 'analytics_data' not in st.session_state:
    st.session_state.analytics_data = None


def fetch_available_countries():
    """Fetch available countries from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/available_countries", timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.session_state.available_countries = data.get("countries", {})
        else:
            # Fallback to default countries
            st.session_state.available_countries = COUNTRY_FLAGS.copy()
    except:
        st.session_state.available_countries = COUNTRY_FLAGS.copy()


def fetch_available_languages():
    """Fetch available languages from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/available_languages", timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.session_state.available_languages = data.get("languages", {})
        else:
            # Fallback to default languages
            st.session_state.available_languages = LANGUAGE_FLAGS.copy()
    except:
        st.session_state.available_languages = LANGUAGE_FLAGS.copy()


def fetch_news():
    """Fetch news headlines from backend with country and language filters"""
    logger.info(
        f"Fetching news for country: {st.session_state.selected_country}, language: {st.session_state.selected_language}")
    try:
        params = {
            "limit": limit,
            "country": st.session_state.selected_country,
            "language": st.session_state.selected_language
        }

        if section != "home":
            params["section"] = section
        if query:
            params["query"] = query

        res = requests.get(f"{BACKEND_URL}/scrape_news", params=params, timeout=30)
        data = res.json()
        headlines = data.get("headlines", [])

        if headlines:
            logger.info(
                f"Fetched {len(headlines)} headlines from {data.get('country_name', 'Unknown')} in {data.get('language_name', 'Unknown')}")
            st.session_state.headlines = headlines
            st.session_state.summary = ""  # Clear previous summary
            st.session_state.current_country = data.get('country_name', 'Unknown')
            st.session_state.current_country_code = data.get('country', 'US')
            st.session_state.current_language = data.get('language_name', 'English')
            st.session_state.current_language_code = data.get('language', 'en')
            return True
        else:
            st.warning("No news found. Try different filters, country, or language.")
            return False

    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        st.error("Failed to fetch news. Make sure the backend server is running.")
        return False


def fetch_analytics():
    """Fetch analytics data from backend"""
    try:
        params = {
            "limit": 50,  # Get more headlines for better analytics
            "country": st.session_state.selected_country,
            "language": st.session_state.selected_language
        }

        if section != "home":
            params["section"] = section
        if query:
            params["query"] = query

        response = requests.get(f"{BACKEND_URL}/news_analytics", params=params, timeout=30)
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        return {"error": str(e)}


def stream_summary() -> Generator[str, None, None]:
    """Stream summary from backend"""
    try:
        st.session_state.stop_streaming = False

        response = requests.post(
            f"{BACKEND_URL}/summarize",
            json={
                "texts": [item['title'] for item in st.session_state.headlines],
                "stream": True,
                "model": MODEL_MAP[model_choice]
            },
            stream=True,
            timeout=120
        )

        response.raise_for_status()

        for line in response.iter_lines():
            # Check if user requested to stop streaming
            if st.session_state.stop_streaming:
                logger.info("Streaming stopped by user")
                yield "\n\n🚫 Streaming stopped by user."
                break

            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                        if 'chunk' in data:
                            yield data['chunk']
                        if data.get('done'):
                            break
                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        yield f"❌ Error: {str(e)}"


def stop_streaming():
    """Stop the ongoing streaming"""
    st.session_state.stop_streaming = True
    st.session_state.is_streaming = False
    logger.info("Stop streaming requested")


# Fetch available countries and languages on startup
if not st.session_state.available_countries:
    fetch_available_countries()
if not st.session_state.available_languages:
    fetch_available_languages()

st.markdown('<h1 class="main-header">Gamma News Topic Tracker</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📍 Country & Region")
st.sidebar.markdown("Select a country to get localized news:")

# Country selection with flags
country_options = []
for code, name in st.session_state.available_countries.items():
    flag = COUNTRY_FLAGS.get(code, "🌐")
    country_options.append(f"{flag} {name} ({code.upper()})")

selected_country_display = st.sidebar.selectbox(
    "Select Country",
    options=country_options,
    index=0,  # Default to US
    help="Choose a country to get localized news coverage"
)

# Extract country code from selection
selected_country_code = selected_country_display.split("(")[-1].replace(")", "").strip().lower()
st.session_state.selected_country = selected_country_code

# Language selection
st.sidebar.header("🗣️ Language")
st.sidebar.markdown("Select a language for news content:")

# Language selection with flags
language_options = []
for code, name in st.session_state.available_languages.items():
    flag = LANGUAGE_FLAGS.get(code, "🌐")
    language_options.append(f"{flag} {name} ({code})")

selected_language_display = st.sidebar.selectbox(
    "Select Language",
    options=language_options,
    index=0,  # Default to English
    help="Choose a language for news content"
)

# Extract language code from selection
selected_language_code = selected_language_display.split("(")[-1].replace(")", "").strip().lower()
st.session_state.selected_language = selected_language_code

st.sidebar.header("📊 News Filters")
section = st.sidebar.selectbox("Select Section",
                               ["home", "world", "business", "technology", "science", "sports", "health"],
                               help="Choose a news category")
query = st.sidebar.text_input("🔍 Search Keywords",
                              help="Enter specific keywords to search for")
limit = st.sidebar.slider("📈 Number of headlines", min_value=5, max_value=50, value=15,
                          help="How many headlines to fetch")

st.sidebar.header("⚡ Summarization Settings")
model_choice = st.sidebar.selectbox(
    "Model Speed",
    ["fastest", "balanced", "quality", "tiny"],
    index=0,
    help="Faster models are less accurate but quicker"
)

# Model mapping
MODEL_MAP = {
    "fastest": "llama3.2:1b",
    "balanced": "llama3.2:3b",
    "quality": "qwen2:7b",
    "tiny": "phi3:mini"
}

# Main layout with tabs
tab1, tab3 = st.tabs(["📰 News", "📊 Analytics"])

with tab1:
    st.subheader("📰 News Controls")

    # Display current country and language badges
    current_flag = COUNTRY_FLAGS.get(st.session_state.selected_country, "🌐")
    current_lang_flag = LANGUAGE_FLAGS.get(st.session_state.selected_language, "🗣️")

    col1a, col1b = st.columns(2)
    with col1a:
        st.markdown(
            f'<div class="country-badge">{current_flag} Country: {st.session_state.selected_country.upper()}</div>',
            unsafe_allow_html=True)
    with col1b:
        st.markdown(
            f'<div class="language-badge">{current_lang_flag} Language: {st.session_state.selected_language.upper()}</div>',
            unsafe_allow_html=True)

    if st.button("🔄 Fetch Latest News", type="secondary", use_container_width=True):
        if fetch_news():
            st.success(
                f"✅ News fetched from {st.session_state.selected_country.upper()} in {st.session_state.selected_language.upper()} successfully!")

    if st.session_state.headlines:
        st.subheader(f"📋 Top {len(st.session_state.headlines)} Headlines")

        for i, item in enumerate(st.session_state.headlines, 1):
            with st.expander(f"{i}. {item['title'][:80]}..."):
                st.markdown(f"**Title:** {item['title']}")
                if item.get('source'):
                    st.markdown(f"**Source:** {item['source']}")
                if item.get('published'):
                    st.markdown(f"**Published:** {item['published']}")
                if item['url']:
                    st.markdown(f"**URL:** [{item['url'][:50]}...]({item['url']})")

# with tab2:
#     st.subheader("🧠 Summary")

#     if st.session_state.headlines:
#         # Stop streaming button (only show when streaming)
#         if st.session_state.is_streaming:
#             if st.button("⏹️ Stop Streaming", type="primary", use_container_width=True):
#                 stop_streaming()

#         if st.button("🚀 Generate Summary", type="secondary",
#                      use_container_width=True) and not st.session_state.is_streaming:
#             st.session_state.is_streaming = True
#             st.session_state.summary = ""
#             st.session_state.stop_streaming = False

#             # Create summary container
#             summary_container = st.empty()
#             summary_container.markdown('<div class="summary-box">', unsafe_allow_html=True)

#             # Streaming indicator
#             st.info("🎯 Streaming summary... (Live) - Click 'Stop Streaming' to interrupt")

#             # Collect and display streaming chunks
#             full_summary = ""
#             for chunk in stream_summary():
#                 if st.session_state.stop_streaming:
#                     break

#                 if "❌ Error:" in chunk:
#                     st.error(chunk)
#                     break

#                 full_summary += chunk
#                 st.session_state.summary = full_summary

#                 # Update the display with proper formatting
#                 summary_container.markdown(
#                     f'<div class="summary-box">'
#                     f'<span class="streaming-indicator"></span>'
#                     f'<strong>Live Summary for {st.session_state.selected_country.upper()} in {st.session_state.selected_language.upper()}:</strong><br><br>{full_summary}'
#                     f'</div>',
#                     unsafe_allow_html=True
#                 )

#                 time.sleep(0.02)

#             st.session_state.is_streaming = False

#             if not st.session_state.stop_streaming:
#                 st.success("✅ Summary complete!")

#             # Final formatted summary
#             summary_container.markdown(
#                 f'<div class="summary-box">'
#                 f'<strong>📊 Summary for {st.session_state.selected_country.upper()} in {st.session_state.selected_language.upper()}:</strong><br><br>{st.session_state.summary}'
#                 f'</div>',
#                 unsafe_allow_html=True
#             )

#         elif st.session_state.summary and not st.session_state.is_streaming:
#             st.markdown(
#                 f'<div class="summary-box">'
#                 f'<strong>📊 Summary for {st.session_state.selected_country.upper()} in {st.session_state.selected_language.upper()}:</strong><br><br>{st.session_state.summary}'
#                 f'</div>',
#                 unsafe_allow_html=True
#             )

#     else:
#         st.info("👆 Fetch some news first to generate a summary!")

with tab3:
    st.subheader("📊 News Analytics")

    if st.button("📈 Generate Analytics", type="primary"):
        with st.spinner("Analyzing news data..."):
            st.session_state.analytics_data = fetch_analytics()

    if st.session_state.analytics_data and "error" not in st.session_state.analytics_data:
        data = st.session_state.analytics_data

        # Display basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Headlines", data["total_headlines"])
        with col2:
            st.metric("Country", data["country"])
        with col3:
            st.metric("Language", data["language"])

        # Word frequency chart
        if data["word_frequency"]:
            st.subheader("📊 Top Keywords")
            word_df = pd.DataFrame(list(data["word_frequency"].items()), columns=["Word", "Frequency"])
            fig = px.bar(word_df, x="Word", y="Frequency", title="Most Frequent Words in Headlines")
            st.plotly_chart(fig, use_container_width=True)

        # Source distribution chart
        if data["source_distribution"]:
            st.subheader("📰 News Sources")
            source_df = pd.DataFrame(list(data["source_distribution"].items()), columns=["Source", "Count"])
            fig = px.pie(source_df, values="Count", names="Source", title="News Source Distribution")
            st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.analytics_data and "error" in st.session_state.analytics_data:
        st.error(f"Error generating analytics: {st.session_state.analytics_data['error']}")
    else:
        st.info("👆 Click 'Generate Analytics' to see visualizations of the news data")

# Footer with country and language info
st.sidebar.markdown("---")
st.sidebar.info(
    f"""
    **📍 Current Country:** {st.session_state.selected_country.upper()}
    **🗣️ Current Language:** {st.session_state.selected_language.upper()}
    **🌐 Available:** {len(st.session_state.available_countries)} countries
    **🗣️ Languages:** {len(st.session_state.available_languages)} options

    **💡 Tips:**
    - Use country filter for localized news
    - Use language filter for content in specific languages
    - Check the Analytics tab for data visualizations
    - 'fastest' model for quick summaries
    - 'quality' model for detailed analysis
    - Click 'Stop Streaming' to interrupt long summaries
    """
)

# Debug info
with st.sidebar.expander("🔧 Debug Info"):
    st.write(f"Selected Country: {st.session_state.selected_country}")
    st.write(f"Selected Language: {st.session_state.selected_language}")
    st.write(f"Available Countries: {len(st.session_state.available_countries)}")
    st.write(f"Available Languages: {len(st.session_state.available_languages)}")
    st.write(f"Backend URL: {BACKEND_URL}")
    st.write(f"Headlines loaded: {len(st.session_state.headlines)}")
    st.write(f"Streaming active: {st.session_state.is_streaming}")