from langchain_community.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.chat_models import ChatOpenAI

# Load the PDF document
pdf_loader = PyPDFLoader("docs/sample.pdf")
docs = pdf_loader.load()

# Create an index
index = VectorstoreIndexCreator().from_documents(docs)

# Initialize chat model
chat_model = ChatOpenAI()

# Function to query the PDF
def chat_with_pdf(query):
    response = index.query(query, llm=chat_model)
    return response

# Example usage
query = "What is the main topic of this document?"
print(chat_with_pdf(query))