import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

class RAGService:
    def __init__(self):
        """Initialize the RAG service"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize Google Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY", "your-api-key-here"),
            temperature=0.3
        )
        
        self.vectorstore = None
        self.qa_chain = None
    
    async def initialize_vectorstore(self, chunks: List[Dict[str, Any]]):
        """Initialize the vector store with document chunks"""
        # Convert chunks to LangChain documents
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk['content'],
                metadata={
                    'id': chunk['id'],
                    'type': chunk['type'],
                    **chunk.get('metadata', {})
                }
            )
            documents.append(doc)
        
        # Create vector store (in-memory ChromaDB)
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=None  # In-memory only
        )
        
        # Create custom prompt template
        prompt_template = """
        You are an AI assistant that helps users understand documents. Use the following context to answer the question.
        
        Context: {context}
        
        Question: {question}
        
        Instructions:
        - Provide accurate and helpful answers based on the context
        - If the context contains image descriptions, incorporate them naturally
        - If you cannot find relevant information in the context, say so clearly
        - Be concise but comprehensive
        - If the context mentions tables or structured data, explain it clearly
        
        Answer:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    async def query(self, question: str) -> str:
        """Query the document using RAG"""
        if not self.qa_chain:
            raise ValueError("Vector store not initialized")
        
        try:
            # Get response from QA chain
            result = self.qa_chain({"query": question})
            
            # Extract answer and sources
            answer = result["result"]
            sources = result.get("source_documents", [])
            
            # Add source information if available
            if sources:
                source_info = "\n\nSources:"
                for i, source in enumerate(sources[:3], 1):  # Limit to top 3 sources
                    source_type = source.metadata.get('type', 'Unknown')
                    source_info += f"\n{i}. {source_type}: {source.page_content[:100]}..."
                
                answer += source_info
            
            return answer
            
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"