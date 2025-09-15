import streamlit as st
import os
import tempfile
from pathlib import Path

st.set_page_config(
    page_title="SOP & Manual RAG Agent",
    page_icon="📚",
    layout="wide"
)

def main():
    st.title("📚 SOP & Manual RAG Agent")
    st.markdown("Upload your product manuals and SOPs, then ask questions to get step-by-step procedures!")
    
    # Check if dependencies are installed
    missing_deps = []
    required_packages = [
        ("openai", "OpenAI API"),
        ("pymupdf", "PDF processing"),
        ("python-dotenv", "Environment variables")
    ]
    
    for package, description in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_deps.append(f"• {package} ({description})")
    
    if missing_deps:
        st.error("Missing required packages:")
        for dep in missing_deps:
            st.write(dep)
        st.info("Please install missing packages using: `pip install --user openai pymupdf python-dotenv`")
        return
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ OpenAI API key not found!")
        st.info("Please set your OpenAI API key in the .env file")
        
        with st.expander("How to set up API key"):
            st.write("""
            1. Create a `.env` file in the project folder
            2. Add this line: `OPENAI_API_KEY=your_api_key_here`
            3. Replace `your_api_key_here` with your actual OpenAI API key
            """)
        return
    
    st.success("✅ All dependencies installed and API key configured!")
    
    # Basic file upload
    st.header("📁 Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload product manuals and SOP documents (PDF format only)"
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} files!")
        for file in uploaded_files:
            st.write(f"• {file.name}")
    
    # Basic question interface
    st.header("🤖 Ask Questions")
    
    user_question = st.text_area(
        "Enter your question:",
        placeholder="e.g., How do I configure emergency notifications?",
        height=100
    )
    
    if st.button("Ask Question", type="primary"):
        if user_question.strip():
            if not uploaded_files:
                st.warning("Please upload some documents first!")
            else:
                with st.spinner("Processing..."):
                    # Placeholder for future RAG implementation
                    st.info("🚧 RAG processing will be implemented once all dependencies are installed successfully!")
                    st.write(f"**Your question:** {user_question}")
                    st.write("**Uploaded files:** " + ", ".join([f.name for f in uploaded_files]))
        else:
            st.warning("Please enter a question")
    
    # Installation instructions
    st.header("🛠️ Complete Setup Instructions")
    
    with st.expander("Step-by-step setup guide"):
        st.markdown("""
        ### 1. Install Full Dependencies
        ```bash
        pip install --user streamlit python-dotenv openai pymupdf pdfplumber chromadb sentence-transformers langchain langchain-openai langchain-community
        ```
        
        ### 2. Set Environment Variables
        Create a `.env` file with:
        ```
        OPENAI_API_KEY=your_openai_api_key_here
        MODEL_NAME=gpt-3.5-turbo
        EMBEDDING_MODEL=text-embedding-ada-002
        ```
        
        ### 3. Run Full App
        ```bash
        streamlit run streamlit_app.py
        ```
        
        ### Troubleshooting
        - If you get permission errors, try adding `--user` flag to pip install
        - If packages conflict, create a virtual environment:
          ```bash
          python -m venv venv
          venv\\Scripts\\activate
          pip install -r requirements.txt
          ```
        """)

if __name__ == "__main__":
    main()