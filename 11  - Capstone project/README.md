Python implementation of an agent that retrieves information from a datasource (e.g., a database or a document store). The agent extracts relevant chunks using semantic search or SQL queries, ensuring that only necessary data is sent to the LLM.

1. Database Querying: Queries a SQLite database, ensuring only the result set is passed to the LLM.
2. Document Chunk Retrieval: Uses FAISS for vector search, retrieving only the most relevant document chunks.
3. LLM Querying: The LLM only receives the extracted context, not the full datasource.
4. Flexible Query Handling: The agent decides whether to query the database, documents, or both.


A Streamlit UI added allowing users to input queries and choose whether to use the database or document retrieval

Added functionality for the agent to call an external API and included corresponding UI elements in Streamlit. 

A sidebar displaying business information, including company name, industry, sales, pending orders, and customer satisfaction.

Added logging throughout the agent's processes, including database queries, document retrieval, API calls, and LLM interactions. 
Logs will be printed to the console for better debugging and monitoring.

Added security countermeasures, including SQL injection prevention, 
improved error handling for API calls, and JSON validation for API payloads.