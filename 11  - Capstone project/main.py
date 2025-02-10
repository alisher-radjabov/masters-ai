import streamlit as st
import logging
import openai
import requests
import sqlite3
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load API key securely
openai.api_key = os.getenv("OPENAI_API_KEY", "your_openai_api_key")


# Function to fetch business information from a database with SQL injection protection
def get_business_info():
    try:
        conn = sqlite3.connect("data/business_data.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT name, revenue FROM business_info LIMIT 1")
        data = cursor.fetchone()
        conn.close()
        return data if data else ("No data available", 0)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return ("Error fetching data", 0)


# Secure function to fetch user-requested business details with parameterized queries
def get_specific_business_info(business_name):
    try:
        conn = sqlite3.connect("data/business_data.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT name, revenue FROM business_info WHERE name = ?", (business_name,))
        data = cursor.fetchone()
        conn.close()
        return data if data else ("No matching business found", 0)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return ("Error fetching data", 0)


# Function to call an external API (e.g., CRM or ticketing system)
def call_external_api(action, params):
    url = "https://api.example.com/action"
    headers = {"Authorization": f"Bearer {os.getenv('API_SECRET_KEY', 'default_key')}",
               "Content-Type": "application/json"}
    try:
        response = requests.post(url, json={"action": action, "params": params}, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API request error: {e}")
        return {"error": "Failed to execute action"}


# Function to interact with the LLM with only partial data
def query_llm(context_chunk):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an assistant providing business insights."},
                      {"role": "user", "content": context_chunk}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"LLM error: {e}")
        return "Error processing request."


# Streamlit UI
def main():
    st.title("AI Business Assistant")
    st.sidebar.header("Business Info")

    # Fetch and display business information
    business_info = get_business_info()
    st.sidebar.text(f"Business Name: {business_info[0]}")
    st.sidebar.text(f"Revenue: {business_info[1]}")

    # Securely fetch specific business information
    business_name_input = st.text_input("Enter business name:")
    if st.button("Fetch Business Details"):
        specific_info = get_specific_business_info(business_name_input)
        st.text(f"Business Name: {specific_info[0]}")
        st.text(f"Revenue: {specific_info[1]}")

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
