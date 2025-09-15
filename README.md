# SOP & Manual RAG Agent

A Retrieval Augmented Generation (RAG) application for querying product manuals and Standard Operating Procedures (SOPs). Upload your documents and ask questions to get step-by-step procedures based on the content.

## Features

- **Multi-Product Support**: Specifically designed for Everbridge, Inner Range, Milestone, and general SOPs
- **Intelligent Document Processing**: Automatic text extraction and chunking from PDF files
- **Smart Product Detection**: Automatically categorizes documents by product type
- **Vector Search**: Semantic search using embeddings for relevant document retrieval
- **Interactive Web Interface**: User-friendly Streamlit interface for document upload and querying
- **Conversation History**: Track your questions and answers
- **Flexible Configuration**: Support for both OpenAI and local embeddings

## Project Structure

```
SOP Agent/
├── src/
│   ├── components/
│   └── utils/
│       ├── document_processor.py    # PDF processing and text extraction
│       ├── vector_store.py         # Vector database management
│       └── rag_agent.py            # RAG logic and LLM integration
├── data/
│   ├── uploads/                    # Temporary file storage
│   └── vectorstore/               # ChromaDB persistence
├── streamlit_app.py               # Main Streamlit application
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   MODEL_NAME=gpt-3.5-turbo
   EMBEDDING_MODEL=text-embedding-ada-002
   ```

4. **Create data directories**:
   ```bash
   mkdir -p data/uploads data/vectorstore
   ```

## Usage

### Starting the Application

Run the Streamlit application:
```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

### Using the Application

1. **Upload Documents**:
   - Use the sidebar to upload PDF files
   - Select the product type (Everbridge, Inner Range, Milestone, or General)
   - Or choose "auto-detect" to let the system categorize automatically
   - Click "Process Documents" to add them to the knowledge base

2. **Ask Questions**:
   - Type your question in the main interface
   - Optionally filter by product type
   - Get step-by-step answers based on your uploaded documents

3. **Manage Documents**:
   - View document status and count in the sidebar
   - Clear all documents if needed
   - Adjust retrieval settings

### Example Questions

- **Everbridge**: "How do I configure emergency notifications in Everbridge?"
- **Inner Range**: "What are the steps to set up access control for a new user?"
- **Milestone**: "How do I configure camera recording schedules?"
- **General SOP**: "What is the procedure for incident escalation?"

## Technical Details

### Document Processing
- Supports PDF files with automatic text extraction
- Uses RecursiveCharacterTextSplitter for intelligent chunking
- Maintains document metadata including source and product type

### Vector Storage
- ChromaDB for local vector storage and persistence
- OpenAI embeddings (with fallback to local SentenceTransformers)
- Metadata filtering for product-specific searches

### RAG Pipeline
- Semantic similarity search for relevant document retrieval
- Context-aware prompt engineering
- GPT-3.5-turbo for answer generation
- Source attribution and transparency

### Web Interface
- Streamlit-based responsive UI
- Real-time document processing
- Conversation history tracking
- Configurable search parameters

## Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `MODEL_NAME`: OpenAI model to use (default: gpt-3.5-turbo)
- `EMBEDDING_MODEL`: Embedding model (default: text-embedding-ada-002)

### Application Settings
- Chunk size and overlap for document processing
- Number of retrieved chunks for context
- Score threshold for similarity search
- Fallback to local embeddings if OpenAI is unavailable

## Troubleshooting

### Common Issues

1. **OpenAI API Key Issues**:
   - Ensure your API key is correctly set in the `.env` file
   - Check that you have sufficient API credits
   - The application will fallback to local embeddings if OpenAI fails

2. **PDF Processing Errors**:
   - Ensure PDFs are not password-protected
   - Some scanned PDFs may not extract text properly
   - Try using different PDF processing tools if needed

3. **Memory Issues**:
   - Large documents may consume significant memory
   - Reduce chunk size or process fewer documents at once
   - Consider upgrading your system memory

4. **Vector Store Issues**:
   - Clear the vector store if you encounter persistence issues
   - Ensure write permissions for the `data/vectorstore` directory

### Performance Tips

- Start with smaller document sets to test the system
- Use product filtering to narrow search scope
- Adjust the number of retrieved chunks based on your needs
- Consider using local embeddings for offline operation

## Dependencies

Key libraries used:
- **Streamlit**: Web interface
- **LangChain**: RAG framework and document processing
- **ChromaDB**: Vector database
- **OpenAI**: LLM and embeddings
- **PyMuPDF/pdfplumber**: PDF processing
- **SentenceTransformers**: Local embeddings fallback

## License

This project is provided as-is for educational and business use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are properly installed
3. Verify your OpenAI API key and credentials
4. Check the console for detailed error messages