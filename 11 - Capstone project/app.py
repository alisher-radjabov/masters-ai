import streamlit as st
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
@dataclass
class Config:
    OPENWEATHER_API_KEY: str = "YOUR_OPENWEATHERMAP_API_KEY"
    NEWSAPI_KEY: str = "YOUR_NEWSAPI_KEY"
    DATASOURCE_FILE: str = "data/companies.json"
    MAX_RESULTS: int = 2

config = Config()

# Data Models
@dataclass
class ChatMessage:
    user_query: str
    agent_response: str
    timestamp: datetime

@dataclass
class CompanyData:
    industry: str
    country: str
    revenue: str
    market_cap: str
    employees: str
    description: str

# Abstract Base Class for Services
class BaseService(ABC):
    @abstractmethod
    def process(self, query: str) -> str:
        pass

# Services
class DatasourceService(BaseService):
    def __init__(self, datasource_file: str):
        self.datasource_file = datasource_file
    
    def process(self, query: str) -> str:
        """Query the local JSON datasource"""
        logger.info(f"Querying datasource with: {query}")
        try:
            results = self._load_and_search(query)
            if results:
                formatted_results = [
                    f"**{result['topic']}**\n{self._format_company_data(result['content'])}"
                    for result in results
                ]
                return "\n\n".join(formatted_results)
            return "No relevant information found in the datasource."
        except Exception as e:
            logger.error(f"Error querying datasource: {e}")
            return "Error accessing datasource."
    
    def _load_and_search(self, query: str) -> List[Dict[str, Any]]:
        """Load JSON file and perform keyword search"""
        try:
            with open(self.datasource_file, 'r') as f:
                data = json.load(f)
            results = [item for item in data if query.lower() in str(item).lower()]
            logger.info(f"Datasource returned {len(results)} results")
            return results[:config.MAX_RESULTS]
        except FileNotFoundError:
            logger.error(f"Datasource file {self.datasource_file} not found")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in datasource file: {e}")
            return []
    
    def _format_company_data(self, content: str) -> str:
        """Format company data for readable display"""
        try:
            parts = [part.strip() for part in content.split('. ')[0].split(', ')]
            details = {}
            for part in parts:
                if ': ' in part:
                    key, value = part.split(': ', 1)
                    details[key] = value
            
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

class WeatherService(BaseService):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def process(self, query: str) -> str:
        """Get weather information for a city"""
        city = self._extract_city(query)
        logger.info(f"Calling OpenWeatherMap API for city: {city}")
        
        if self.api_key == "YOUR_OPENWEATHERMAP_API_KEY":
            return "Weather service not configured. Please add your OpenWeatherMap API key."
        
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            weather = (
                f"Weather in {city}: {data['weather'][0]['description']}, "
                f"{data['main']['temp']}°C (feels like {data['main']['feels_like']}°C)\n"
                f"Humidity: {data['main']['humidity']}% | "
                f"Wind: {data['wind']['speed']} m/s"
            )
            logger.info(f"Weather API response: {weather}")
            return weather
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather: {e}")
            return "Unable to fetch weather data. Please check your connection."
        except KeyError as e:
            logger.error(f"Unexpected weather API response format: {e}")
            return "Unable to parse weather data."
    
    def _extract_city(self, query: str) -> str:
        """Extract city name from query"""
        city = query.replace("weather in", "").replace("weather", "").strip()
        return city if city else "London"

class NewsService(BaseService):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    def process(self, query: str) -> str:
        """Get news articles for a topic"""
        topic = self._extract_topic(query)
        logger.info(f"Calling NewsAPI for topic: {topic}")
        
        if self.api_key == "YOUR_NEWSAPI_KEY":
            return "News service not configured. Please add your NewsAPI key."
        
        try:
            params = {
                'q': topic,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': config.MAX_RESULTS
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'ok' and data['articles']:
                articles = data['articles'][:config.MAX_RESULTS]
                news_items = []
                for article in articles:
                    title = article['title']
                    source = article['source']['name']
                    published_at = article['publishedAt'][:10]  # Get date only
                    news_items.append(f"**{title}**\n*{source} - {published_at}*")
                
                logger.info(f"News API returned {len(news_items)} articles")
                return "\n\n".join(news_items)
            else:
                return f"No news articles found for topic: {topic}"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news: {e}")
            return "Unable to fetch news data. Please check your connection."
        except KeyError as e:
            logger.error(f"Unexpected news API response format: {e}")
            return "Unable to parse news data."
    
    def _extract_topic(self, query: str) -> str:
        """Extract topic from query"""
        topic = query.replace("news about", "").replace("news", "").strip()
        return topic if topic else "technology"

# Query Processor
class QueryProcessor:
    def __init__(self):
        self.datasource_service = DatasourceService(config.DATASOURCE_FILE)
        self.weather_service = WeatherService(config.OPENWEATHER_API_KEY)
        self.news_service = NewsService(config.NEWSAPI_KEY)
    
    def process_query(self, query: str) -> str:
        """Process user query and return appropriate response"""
        logger.info(f"Processing query: {query}")
        query_lower = query.lower().strip()
        
        try:
            if "weather" in query_lower:
                return self.weather_service.process(query_lower)
            elif "news" in query_lower:
                return self.news_service.process(query_lower)
            else:
                return self.datasource_service.process(query_lower)
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return "Sorry, I encountered an error processing your request."

# UI Components
class ChatInterface:
    def __init__(self):
        self.query_processor = QueryProcessor()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def render_sidebar(self):
        """Render the sidebar with business information"""
        with st.sidebar:
            st.header("🏢 Business Information")
            st.info(
                "**Company**: xAI Solutions\n\n"
                "**Status**: 🟢 Operational\n\n"
                f"**Last Updated**: {datetime.now().strftime('%B %d, %Y')}\n\n"
                "**Metrics**:\n"
                "- Active Users: 1,234\n"
                "- Queries Processed: 5,678\n"
                f"- Chat Sessions: {len(st.session_state.chat_history)}"
            )
            
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
    
    def render_main_interface(self):
        """Render the main chat interface"""
        st.title("🤖 Agent Chat Interface")
        st.markdown("Ask about **companies**, **weather**, or **news**. I'm here to help!")
        
        # Example queries
        with st.expander("💡 Example Queries", expanded=False):
            st.markdown(
                "- `Nexlify Technologies`\n"
                "- `weather in Paris`\n"
                "- `news about AI`\n"
                "- `weather in Tokyo`\n"
                "- `news about climate change`"
            )
        
        # Chat input
        user_input = st.text_input(
            "Enter your query:",
            key="user_input",
            placeholder="Type your question here..."
        )
        
        if user_input:
            self._handle_user_input(user_input)
        
        self._display_chat_history()
    
    def _handle_user_input(self, user_input: str):
        """Handle user input and generate response"""
        with st.spinner("Processing your query..."):
            response = self.query_processor.process_query(user_input)
            
            chat_message = ChatMessage(
                user_query=user_input,
                agent_response=response,
                timestamp=datetime.now()
            )
            
            st.session_state.chat_history.append(chat_message)
    
    def _display_chat_history(self):
        """Display chat history"""
        if st.session_state.chat_history:
            st.subheader("💬 Chat History")
            
            # Display most recent first
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.container():
                    st.markdown(f"**🧑 You**: {chat.user_query}")
                    st.markdown(f"**🤖 Agent**:\n{chat.agent_response}")
                    st.caption(f"*{chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*")
                    if i < len(st.session_state.chat_history) - 1:
                        st.divider()

# Main Application
def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Agent Chat Interface",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    chat_interface = ChatInterface()
    chat_interface.render_sidebar()
    chat_interface.render_main_interface()

if __name__ == "__main__":
    main()