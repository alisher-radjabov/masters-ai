import streamlit as st
import logging
import openai
import requests
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI API
openai.api_key = "your_openai_api_key"

# Function to fetch business information from a database
def get_business_info():
    try:
        conn = sqlite3.connect("data/business_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, revenue FROM business_info LIMIT 1")
        data = cursor.fetchone()
        conn.close()
        return data if data else ("No Business Found", 0)
    except Exception as e:
        logging.error(f"Database error: {e}")
        return ("Error fetching data", 0)

# Function to call an external API (e.g., CRM or ticketing system)
def call_external_api(action, params):
    url = "https://api.example.com/action"
    response = requests.post(url, json={"action": action, "params": params})
    return response.json()


# Function to interact with the LLM with only partial data.tables
def query_llm(context_chunk):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an assistant providing business insights."},
                  {"role": "user", "content": context_chunk}]
    )
    return response["choices"][0]["message"]["content"]


# Streamlit UI
def main():
    st.title("AI Business Assistant")
    st.sidebar.header("Business Info")

    # Fetch and display business information
    business_info = get_business_info()
    st.sidebar.text(f"Business Name: {business_info[0]}")
    st.sidebar.text(f"Revenue: {business_info[1]}")

    # Chat input
    user_input = st.text_input("Ask something about the business:")
    if st.button("Submit"):
        logging.info(f"User query: {user_input}")
        response = query_llm(user_input)
        st.text_area("Response:", response)

    # API action execution
    action = st.selectbox("Choose an action:", ["Create Ticket", "Update CRM"])
    param = st.text_input("Enter parameters:")
    if st.button("Execute Action"):
        api_response = call_external_api(action, param)
        logging.info(f"Executed {action} with params {param}")
        st.text(f"API Response: {api_response}")


if __name__ == "__main__":
    main()
