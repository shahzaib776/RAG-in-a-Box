# RAG-in-a-Box

A complete multi-modal Retrieval-Augmented Generation (RAG) system that allows users to upload PDF documents and interact with their content through natural language queries. The system can understand text, tables, and images within PDFs.

## Features

- **Multi-modal Document Processing**: Handles text, tables, and images in PDF documents
- **Image Understanding**: Uses BLIP model for automatic image captioning
- **Ephemeral Sessions**: All data is discarded when users leave (privacy-focused)
- **Modern UI**: Clean, responsive React interface with Tailwind CSS
- **Single Container**: Everything packaged in one Docker container
- **In-memory Vector Store**: Uses ChromaDB for fast, temporary document indexing

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **LangChain**: AI orchestration and RAG pipeline
- **ChromaDB**: In-memory vector database
- **Unstructured**: Advanced PDF parsing with table and image extraction
- **BLIP**: Salesforce's image captioning model
- **BGE**: BAAI's text embedding model
- **Google Gemini Pro**: Large language model for Q&A

### Frontend
- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Type-safe JavaScript
- **Lucide React**: Beautiful icons

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Google API key for Gemini Pro

### Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd rag-in-a-box
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   Open http://localhost:8000 in your browser

### Manual Setup (Development)

1. **Backend setup:**
   ```bash
   pip install -r requirements.txt
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Frontend setup (in another terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Usage

1. **Upload a PDF**: Drag and drop or click to upload a PDF document
2. **Wait for Processing**: The system will extract text, tables, and generate image captions
3. **Start Chatting**: Ask questions about your document's content
4. **New Document**: Click "New Document" to start over with a different file

## API Endpoints

- `POST /api/upload` - Upload and process a PDF file
- `POST /api/chat` - Send a message to chat with the document
- `DELETE /api/session/{session_id}` - Delete a session and clean up resources
- `GET /api/health` - Health check endpoint

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │   FastAPI Backend │    │   AI Services   │
│                 │    │                  │    │                 │
│ • File Upload   │◄──►│ • Session Mgmt   │◄──►│ • Document      │
│ • Chat Interface│    │ • API Endpoints  │    │   Processing    │
│ • Responsive UI │    │ • Static Serving │    │ • Vector Store  │
└─────────────────┘    └──────────────────┘    │ • LLM Queries   │
                                               └─────────────────┘
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Required for Gemini Pro API access
- `ENVIRONMENT`: Set to "production" for deployment optimizations

### Model Configuration

The system uses these pre-configured models:
- **Text Embeddings**: BAAI/bge-small-en-v1.5
- **Image Captioning**: Salesforce/blip-image-captioning-large  
- **Language Model**: Google Gemini Pro
- **Vector Database**: ChromaDB (in-memory)

## Development

### Project Structure
```
rag-in-a-box/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── document_processor.py  # PDF processing
│       └── rag_service.py         # RAG pipeline
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   └── App.tsx         # Main application
│   └── package.json
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Container orchestration
└── requirements.txt        # Python dependencies
```

### Adding New Features

1. **Backend**: Add new endpoints in `backend/main.py`
2. **Frontend**: Create components in `frontend/src/components/`
3. **Services**: Extend processing in `backend/services/`

## Deployment

### Docker Production Build
```bash
docker build -t rag-in-a-box .
docker run -p 8000:8000 -e GOOGLE_API_KEY=your-key rag-in-a-box
```

### Environment Considerations
- Ensure sufficient memory for model loading (4GB+ recommended)
- GPU support can be added for faster image processing
- Consider persistent storage for production logging

## Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce batch sizes or use smaller models
2. **Slow Processing**: Enable GPU support or optimize chunk sizes
3. **API Errors**: Verify Google API key and quota limits

### Logs
```bash
docker-compose logs -f rag-in-a-box
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Unstructured.io for document processing
- Hugging Face for model hosting
- Google for Gemini Pro API
- Salesforce for BLIP model
- BAAI for BGE embeddings