from langchain_community.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from dotenv import load_dotenv
import os
from typing import List, Optional
from langchain.docstore.document import Document

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI()

class PDFChatBot:
    """A class to handle PDF document loading and querying."""
    
    def __init__(self, pdf_path: str, api_key: Optional[str] = None):
        """
        Initialize the PDF chatbot.
        
        Args:
            pdf_path (str): Path to the PDF file
            api_key (str, optional): OpenAI API key
        """
        self.pdf_path = pdf_path
        self.index = None
        self.chat_model = None
        
        try:
            # Initialize chat model
            self.chat_model = ChatOpenAI(
                api_key=api_key or os.getenv("OPENAI_API_KEY"),
                temperature=0.7,
                model_name="gpt-3.5-turbo"
            )

            # Load and index documents
            self._load_and_index()
            
        except Exception as e:
            print(f"Error initializing chatbot: {str(e)}")
            raise

    def _load_and_index(self):
        """Load PDF and create index."""
        try:
            if not os.path.exists(self.pdf_path):
                raise FileNotFoundError(f"PDF file not found at: {self.pdf_path}")
                
            # Load PDF documents
            pdf_loader = PyPDFLoader(self.pdf_path)
            docs: List[Document] = pdf_loader.load()
            
            if not docs:
                raise ValueError("No content could be extracted from the PDF")
                
            # Create index
            self.index = VectorstoreIndexCreator().from_documents(docs)
            
        except Exception as e:
            print(f"Error loading/indexing PDF: {str(e)}")
            raise

    def query(self, question: str) -> str:
        """
        Query the PDF document with a question.
        
        Args:
            question (str): The question to ask about the document
            
        Returns:
            str: The response from the chat model
        """
        try:
            if not question.strip():
                raise ValueError("Query cannot be empty")
                
            response = self.index.query(question, llm=self.chat_model)
            return response or "No response generated"
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return f"Error: {str(e)}"

if __name__ == "__main__":
    try:
        pdf_path = "docs/burgers.pdf"
        chatbot = PDFChatBot(pdf_path)
        query = "What is the main topic of this document?"
        response = chatbot.query(query)
        print(f"Query: {query}")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")