import os
import chromadb
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer

class VectorStoreManager:
    def __init__(self, persist_directory: str = "./data/vectorstore", use_openai: bool = True):
        self.persist_directory = persist_directory
        self.use_openai = use_openai
        
        if use_openai:
            try:
                self.embeddings = OpenAIEmbeddings()
            except Exception as e:
                print(f"OpenAI embeddings failed: {e}, falling back to local model")
                self.use_openai = False
                self.embeddings = self._get_local_embeddings()
        else:
            self.embeddings = self._get_local_embeddings()
        
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _get_local_embeddings(self):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        class LocalEmbeddings:
            def __init__(self, model):
                self.model = model
            
            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                return self.model.encode(texts).tolist()
            
            def embed_query(self, text: str) -> List[float]:
                return self.model.encode([text])[0].tolist()
        
        return LocalEmbeddings(model)
    
    def _initialize_vectorstore(self):
        os.makedirs(self.persist_directory, exist_ok=True)
        
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        except Exception as e:
            print(f"Error initializing vectorstore: {e}")
            self.vectorstore = None
    
    def add_documents(self, documents: List[Document]) -> bool:
        if not self.vectorstore:
            print("Vectorstore not initialized")
            return False
        
        try:
            self.vectorstore.add_documents(documents)
            self.vectorstore.persist()
            print(f"Added {len(documents)} documents to vectorstore")
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search_documents(self, 
                        query: str, 
                        k: int = 5, 
                        product_filter: str = None,
                        score_threshold: float = 0.5) -> List[Document]:
        if not self.vectorstore:
            print("Vectorstore not initialized")
            return []
        
        try:
            filter_dict = {}
            if product_filter and product_filter != "all":
                filter_dict["product_type"] = product_filter
            
            if filter_dict:
                results = self.vectorstore.similarity_search_with_score(
                    query, k=k, filter=filter_dict
                )
            else:
                results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            filtered_results = []
            for doc, score in results:
                if score <= score_threshold:
                    filtered_results.append(doc)
            
            return filtered_results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_document_count(self) -> int:
        if not self.vectorstore:
            return 0
        
        try:
            collection = self.vectorstore._collection
            return collection.count()
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0
    
    def get_products(self) -> List[str]:
        if not self.vectorstore:
            return []
        
        try:
            collection = self.vectorstore._collection
            results = collection.get()
            
            products = set()
            if results and 'metadatas' in results:
                for metadata in results['metadatas']:
                    if metadata and 'product_type' in metadata:
                        products.add(metadata['product_type'])
            
            return list(products)
            
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
    
    def clear_vectorstore(self) -> bool:
        try:
            if os.path.exists(self.persist_directory):
                import shutil
                shutil.rmtree(self.persist_directory)
            
            self._initialize_vectorstore()
            print("Vectorstore cleared successfully")
            return True
            
        except Exception as e:
            print(f"Error clearing vectorstore: {e}")
            return False