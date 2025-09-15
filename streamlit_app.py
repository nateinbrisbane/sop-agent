import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import List

from src.utils.document_processor import DocumentProcessor
from src.utils.vector_store import VectorStoreManager
from src.utils.rag_agent import RAGAgent

st.set_page_config(
    page_title="SOP & Manual RAG Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def initialize_components():
    """Initialize the RAG components"""
    try:
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
        vector_store = VectorStoreManager(persist_directory="./data/vectorstore")
        agent = RAGAgent(vector_store)
        return processor, vector_store, agent
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        return None, None, None

def main():
    st.title("📚 SOP & Manual RAG Agent")
    st.markdown("Upload your product manuals and SOPs, then ask questions to get step-by-step procedures!")
    
    processor, vector_store, agent = initialize_components()
    
    if not all([processor, vector_store, agent]):
        st.error("Failed to initialize the application. Please check your configuration.")
        return
    
    with st.sidebar:
        st.header("📁 Document Management")
        
        tab1, tab2, tab3 = st.tabs(["Upload", "Status", "Settings"])
        
        with tab1:
            st.subheader("Upload Documents")
            
            uploaded_files = st.file_uploader(
                "Choose PDF files",
                type=['pdf'],
                accept_multiple_files=True,
                help="Upload product manuals and SOP documents (PDF format only)"
            )
            
            product_types = ["auto-detect", "everbridge", "inner_range", "milestone", "general"]
            selected_product = st.selectbox(
                "Product Type",
                product_types,
                help="Select the product type or let the system auto-detect"
            )
            
            if st.button("Process Documents", type="primary"):
                if uploaded_files:
                    process_uploaded_files(uploaded_files, selected_product, processor, vector_store)
                else:
                    st.warning("Please upload at least one PDF file")
        
        with tab2:
            st.subheader("Document Status")
            
            doc_count = vector_store.get_document_count()
            st.metric("Total Document Chunks", doc_count)
            
            products = vector_store.get_products()
            if products:
                st.write("**Available Products:**")
                for product in products:
                    st.write(f"• {product.replace('_', ' ').title()}")
            
            if st.button("Clear All Documents", type="secondary"):
                if st.confirm("Are you sure you want to clear all documents?"):
                    vector_store.clear_vectorstore()
                    st.success("All documents cleared!")
                    st.rerun()
        
        with tab3:
            st.subheader("Settings")
            
            search_k = st.slider(
                "Number of relevant chunks to retrieve",
                min_value=1,
                max_value=10,
                value=5,
                help="Higher values provide more context but may include less relevant information"
            )
            
            st.session_state.search_k = search_k
    
    st.header("🤖 Ask Questions")
    
    available_products = ["all"] + vector_store.get_products()
    product_filter = st.selectbox(
        "Filter by Product",
        available_products,
        format_func=lambda x: "All Products" if x == "all" else x.replace('_', ' ').title()
    )
    
    if product_filter != "all":
        help_text = agent.get_product_specific_help(product_filter)
        st.info(f"💡 **Tip for {product_filter.replace('_', ' ').title()}:** {help_text}")
    
    user_question = st.text_area(
        "Enter your question:",
        placeholder="e.g., How do I configure emergency notifications in Everbridge?",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("Ask Question", type="primary"):
            if user_question.strip():
                ask_question(user_question, product_filter, agent)
            else:
                st.warning("Please enter a question")
    
    with col2:
        if st.button("Clear Conversation"):
            if 'conversation_history' in st.session_state:
                del st.session_state.conversation_history
            st.rerun()
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if st.session_state.conversation_history:
        st.header("💬 Conversation History")
        
        for i, (question, response) in enumerate(reversed(st.session_state.conversation_history)):
            with st.expander(f"Q: {question[:100]}{'...' if len(question) > 100 else ''}", expanded=(i == 0)):
                st.write("**Question:**")
                st.write(question)
                
                st.write("**Answer:**")
                st.write(response['answer'])
                
                if response.get('sources'):
                    st.write("**Sources:**")
                    for j, source in enumerate(response['sources'], 1):
                        st.write(f"{j}. {source['source']} (Product: {source['product_type']})")

def process_uploaded_files(uploaded_files, selected_product, processor, vector_store):
    """Process uploaded files and add to vector store"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_documents = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            status_text.text(f"Processing {uploaded_file.name}...")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            
            product_type = None if selected_product == "auto-detect" else selected_product
            
            documents = processor.process_document(tmp_file_path, product_type)
            all_documents.extend(documents)
            
            os.unlink(tmp_file_path)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")
            continue
    
    if all_documents:
        status_text.text("Adding documents to vector store...")
        
        success = vector_store.add_documents(all_documents)
        
        if success:
            st.success(f"Successfully processed {len(uploaded_files)} files and added {len(all_documents)} document chunks!")
        else:
            st.error("Failed to add documents to vector store")
    else:
        st.error("No documents were successfully processed")
    
    progress_bar.empty()
    status_text.empty()

def ask_question(question, product_filter, agent):
    """Process user question and generate response"""
    
    validation = agent.validate_query(question)
    if not validation['valid']:
        st.error(validation['message'])
        return
    
    with st.spinner("Searching documents and generating answer..."):
        search_k = getattr(st.session_state, 'search_k', 5)
        
        response = agent.generate_answer(
            query=question,
            product_filter=product_filter if product_filter != "all" else None,
            k=search_k
        )
    
    st.session_state.conversation_history.append((question, response))
    
    st.success("Answer generated successfully!")
    
    with st.container():
        st.write("**Answer:**")
        st.write(response['answer'])
        
        if response.get('sources'):
            with st.expander(f"📄 Sources ({len(response['sources'])} documents)", expanded=False):
                for i, source in enumerate(response['sources'], 1):
                    st.write(f"**{i}.** {source['source']} (Product: {source['product_type']}, Chunk: {source['chunk_index']})")

if __name__ == "__main__":
    main()