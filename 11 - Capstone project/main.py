import streamlit as st
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to load and query datasource (JSON)
def query_datasource(query):
    logger.info(f"Querying datasource with: {query}")
    try:
        with open('data/companies.json', 'r') as f:
            data = json.load(f)
        # Simple keyword-based search in JSON
        results = [item for item in data if query.lower() in str(item).lower()]
        logger.info(f"Datasource returned {len(results)} results")
        return results[:2]  # Return up to 2 results
    except Exception as e:
        logger.error(f"Error querying datasource: {e}")
        return []

# Function to call OpenWeatherMap API
def get_weather(city):
    api_key = os.getenv("OPENAI_API_KEY") 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    logger.info(f"Calling OpenWeatherMap API for city: {city}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather = f"Weather in {city}: {data['weather'][0]['description']}, {data['main']['temp']}°C"
        logger.info(f"Weather API response: {weather}")
        return weather
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return "Unable to fetch weather data."

# Function to call NewsAPI
def get_news(topic):
    api_key = os.getenv("OPENAI_API_KEY")
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={api_key}&language=en"
    logger.info(f"Calling NewsAPI for topic: {topic}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data['articles'][:2]
        news = [f"{article['title']} - {article['source']['name']}" for article in articles]
        logger.info(f"News API returned {len(news)} articles")
        return "\n".join(news)
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return "Unable to fetch news data."

# Function to format company data for readable display
def format_company_data(content):
    try:
        parts = [part.strip() for part in content.split('. ')[0].split(', ')]
        details = {part.split(': ')[0]: part.split(': ')[1] for part in parts}
        description = content.split('. ')[1] if len(content.split('. ')) > 1 else ""
        formatted = (
            f"- **Industry**: {details.get('Industry', 'N/A')}\n"
            f"- **Country**: {details.get('Country', 'N/A')}\n"
            f"- **Revenue**: {details.get('Revenue', 'N/A')}\n"
            f"- **Market Cap**: {details.get('Market Cap', 'N/A')}\n"
            f"- **Employees**: {details.get('Employees', 'N/A')}\n"
            f"- **Description**: {description}"
        )
        return formatted
    except Exception as e:
        logger.error(f"Error formatting company data: {e}")
        return content

# Function to process user query
def process_query(query):
    logger.info(f"Processing query: {query}")
    query = query.lower().strip()

    if "weather" in query:
        city = query.replace("weather in", "").strip() or "London"
        return get_weather(city)
    elif "news about" in query:
        topic = query.replace("news about", "").strip() or "technology"
        return get_news(topic)
    else:
        results = query_datasource(query)
        if results:
            formatted_results = [
                f"**{result['topic']}**\n{format_company_data(result['content'])}"
                for result in results
            ]
            return "\n\n".join(formatted_results)
        return "No relevant information found in the datasource."

# Streamlit UI
st.title("Agent Chat Interface")
st.markdown("Interact with the agent to query company data, weather, or news.")

# Sidebar for business information
with st.sidebar:
    st.header("Business Information")
    st.write("**Company**: xAI Solutions")
    st.write("**Status**: Operational")
    st.write("**Last Updated**: August 7, 2025")
    st.write("**Metrics**:")
    st.write("- Active Users: 1,234")
    st.write("- Queries Processed: 5,678")

# Chat interface
st.subheader("Chat with the Agent")
st.markdown("Ask about companies, weather, or news. Example: 'Nexlify Technologies', 'weather in Paris', 'news about AI'.")
user_input = st.text_input("Enter your query:", key="user_input")

if user_input:
    response = process_query(user_input)
    st.session_state.chat_history.append({"user": user_input, "agent": response})

    # Display chat history with last result at the top
    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"**You**: {chat['user']}")
        st.markdown(f"**Agent**:\n{chat['agent']}")
        st.markdown("---")