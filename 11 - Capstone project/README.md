# Agent Chat

A Python-based agent with a Streamlit UI that queries a local datasource and integrates with external APIs (OpenWeatherMap and NewsAPI).

## Prerequisites
- Python <= 3.12 (recommended: 3.11)

## Installation


### **Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Set Up API Keys**
Create a `.env` file in the project root and add your **OpenAI API key**:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### **Agent Chat*
```bash
streamlit run main.py
```