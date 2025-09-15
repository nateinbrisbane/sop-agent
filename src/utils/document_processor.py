import os
import fitz
import pdfplumber
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        self.supported_products = ["everbridge", "inner_range", "milestone", "general"]
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error with pdfplumber: {e}, trying PyMuPDF...")
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
            except Exception as e2:
                print(f"Error with PyMuPDF: {e2}")
                raise Exception(f"Could not extract text from PDF: {e2}")
        
        return text.strip()
    
    def detect_product_type(self, text: str, filename: str) -> str:
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        if "everbridge" in text_lower or "everbridge" in filename_lower:
            return "everbridge"
        elif "inner range" in text_lower or "inner_range" in filename_lower or "innerrange" in filename_lower:
            return "inner_range"
        elif "milestone" in text_lower or "milestone" in filename_lower:
            return "milestone"
        else:
            return "general"
    
    def process_document(self, file_path: str, product_type: str = None) -> List[Document]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("Currently only PDF files are supported")
        
        text = self.extract_text_from_pdf(file_path)
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
        
        filename = os.path.basename(file_path)
        
        if product_type is None:
            product_type = self.detect_product_type(text, filename)
        
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": filename,
                "file_path": file_path,
                "product_type": product_type,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            documents.append(Document(page_content=chunk, metadata=metadata))
        
        return documents
    
    def process_multiple_documents(self, file_paths: List[str], product_types: Dict[str, str] = None) -> List[Document]:
        all_documents = []
        
        for file_path in file_paths:
            try:
                product_type = None
                if product_types and file_path in product_types:
                    product_type = product_types[file_path]
                
                documents = self.process_document(file_path, product_type)
                all_documents.extend(documents)
                print(f"Processed {len(documents)} chunks from {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        return all_documents