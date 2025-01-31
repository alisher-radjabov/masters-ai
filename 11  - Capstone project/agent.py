import streamlit as st
import sqlite3
import requests
import logging
import json
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DataAgent:
    def __init__(self, db_path="data/data.db", doc_path=None):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.retriever = None

        logging.info("Initializing DataAgent with database: %s", db_path)

        if doc_path:
            logging.info("Setting up vector store from document: %s", doc_path)
            self._setup_vector_store(doc_path)

    def _setup_vector_store(self, doc_path):
        """Loads documents, splits them into chunks, and creates a vector store."""
        loader = TextLoader(doc_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(docs, embeddings)
        self.retriever = vectorstore.as_retriever()
        logging.info("Vector store setup complete.")

    def query_database(self, sql_query):
        """Executes SQL queries safely and returns results."""
        logging.info("Executing SQL query: %s", sql_query)
        try:
            if any(keyword in sql_query.lower() for keyword in ["drop", "delete", "update", "insert", "alter"]):
                raise ValueError("Unsafe SQL query detected.")
            self.cursor.execute(sql_query)
            result = self.cursor.fetchall()
            logging.info("Query Result: %s", result)
            return result
        except (sqlite3.Error, ValueError) as e:
            logging.error("Database error: %s", e)
            return f"Database error: {e}"

    def query_documents(self, query):
        """Retrieves relevant document chunks."""
        logging.info("Retrieving documents for query: %s", query)
        if self.retriever:
            result = self.retriever.get_relevant_documents(query)
            logging.info("Document Retrieval Result: %s", result)
            return result
        return "No document retriever is set up."

    def query_llm(self, query, context):
        """Queries the LLM with extracted context."""
        logging.info("Querying LLM with context: %s", context)
        llm = OpenAI()
        prompt = f"Context: {context}\nUser Query: {query}\nAnswer:"
        response = llm(prompt)
        logging.info("LLM Response: %s", response)
        return response

    def call_external_api(self, endpoint, payload):
        """Calls a 3rd party API to perform an action with error handling."""
        logging.info("Calling external API: %s with payload: %s", endpoint, payload)
        try:
            response = requests.post(endpoint, json=json.loads(payload))
            result = response.json()
            logging.info("API Response: %s", result)
            return result
        except (requests.RequestException, json.JSONDecodeError) as e:
            logging.error("API call failed: %s", e)
            return f"API call failed: {e}"

    def handle_query(self, query, use_db=True, use_docs=True, use_api=False, api_endpoint=None, api_payload=None):
        """Determines the best approach to retrieve data and respond."""
        logging.info("Handling user query: %s", query)
        context = ""

        if use_db:
            db_result = self.query_database(query)
            context += f"Database Result: {db_result}\n"

        if use_docs:
            doc_result = self.query_documents(query)
            context += f"Document Result: {doc_result}\n"

        if use_api and api_endpoint:
            api_result = self.call_external_api(api_endpoint, api_payload or "{}")
            context += f"API Result: {api_result}\n"

        return self.query_llm(query, context)


# Streamlit UI
st.set_page_config(page_title="Data Query Assistant", layout="wide")
st.title("Data Query Assistant")

# Business Information Section
st.sidebar.header("Business Overview")
st.sidebar.write("**Company:** Example Corp")
st.sidebar.write("**Industry:** Technology")
st.sidebar.write("**Current Quarter Sales:** $1.2M")
st.sidebar.write("**Pending Orders:** 150")
st.sidebar.write("**Customer Satisfaction:** 92%")

st.subheader("Query the Data")

agent = DataAgent(db_path="data/data.db", doc_path="docs/sample.txt")

query = st.text_input("Enter your query:")
use_db = st.checkbox("Use Database", value=True)
use_docs = st.checkbox("Use Documents", value=True)
use_api = st.checkbox("Call External API", value=False)
api_endpoint = st.text_input("API Endpoint (if applicable):")
api_payload = st.text_area("API Payload (JSON format, optional):")

if st.button("Submit"):
    logging.info("User submitted query: %s", query)
    response = agent.handle_query(query, use_db=use_db, use_docs=use_docs, use_api=use_api, api_endpoint=api_endpoint,
                                  api_payload=api_payload)
    logging.info("Final Response: %s", response)
    st.write("### Response:")
    st.write(response)
