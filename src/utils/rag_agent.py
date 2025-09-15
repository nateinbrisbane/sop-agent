import os
from typing import List, Dict, Any, Optional
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

class RAGAgent:
    def __init__(self, vector_store_manager, model_name: str = "gpt-3.5-turbo"):
        self.vector_store = vector_store_manager
        self.model_name = model_name
        
        try:
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=0.1,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        except Exception as e:
            print(f"Error initializing OpenAI model: {e}")
            self.llm = None
        
        self.prompt_template = self._create_prompt_template()
    
    def _create_prompt_template(self) -> PromptTemplate:
        template = """You are a helpful assistant that provides step-by-step procedures based on product manuals and Standard Operating Procedures (SOPs).

Context from relevant documents:
{context}

Human Question: {question}

Instructions:
1. Analyze the provided context carefully
2. If the question is about a specific procedure, provide clear step-by-step instructions
3. Reference the specific document/manual when possible
4. If the context doesn't contain enough information, say so clearly
5. Focus on actionable steps and procedures
6. Include any safety warnings or important notes from the source material

Answer:"""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def retrieve_relevant_documents(self, 
                                  query: str, 
                                  product_filter: str = None, 
                                  k: int = 5) -> List[Document]:
        return self.vector_store.search_documents(
            query=query,
            k=k,
            product_filter=product_filter
        )
    
    def format_context(self, documents: List[Document]) -> str:
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            source = metadata.get('source', 'Unknown')
            product_type = metadata.get('product_type', 'Unknown')
            
            context_part = f"""
Document {i}:
Source: {source} (Product: {product_type})
Content: {doc.page_content}
---"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def generate_answer(self, 
                       query: str, 
                       product_filter: str = None, 
                       k: int = 5) -> Dict[str, Any]:
        if not self.llm:
            return {
                "answer": "Error: Language model not available. Please check your OpenAI API key.",
                "sources": [],
                "product_filter": product_filter
            }
        
        relevant_docs = self.retrieve_relevant_documents(
            query=query,
            product_filter=product_filter,
            k=k
        )
        
        if not relevant_docs:
            return {
                "answer": f"I couldn't find relevant information in the uploaded documents for your query about: '{query}'. Please make sure you have uploaded the appropriate manuals or SOPs, or try rephrasing your question.",
                "sources": [],
                "product_filter": product_filter
            }
        
        context = self.format_context(relevant_docs)
        
        try:
            prompt = self.prompt_template.format(
                context=context,
                question=query
            )
            
            response = self.llm.predict(prompt)
            
            sources = []
            for doc in relevant_docs:
                metadata = doc.metadata
                sources.append({
                    "source": metadata.get('source', 'Unknown'),
                    "product_type": metadata.get('product_type', 'Unknown'),
                    "chunk_index": metadata.get('chunk_index', 0)
                })
            
            return {
                "answer": response.strip(),
                "sources": sources,
                "product_filter": product_filter,
                "num_sources": len(relevant_docs)
            }
            
        except Exception as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "sources": [],
                "product_filter": product_filter
            }
    
    def get_product_specific_help(self, product_type: str) -> str:
        help_text = {
            "everbridge": "Ask about emergency notification procedures, system configuration, or incident management using Everbridge.",
            "inner_range": "Ask about access control procedures, system setup, or security management using Inner Range systems.",
            "milestone": "Ask about video surveillance procedures, camera configuration, or system management using Milestone.",
            "general": "Ask about any general procedures or SOPs from your uploaded documents."
        }
        
        return help_text.get(product_type, "Ask about procedures related to your uploaded documents.")
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        if not query or len(query.strip()) < 3:
            return {
                "valid": False,
                "message": "Please enter a more specific question (at least 3 characters)."
            }
        
        if len(query) > 1000:
            return {
                "valid": False,
                "message": "Question is too long. Please keep it under 1000 characters."
            }
        
        return {
            "valid": True,
            "message": "Query is valid."
        }