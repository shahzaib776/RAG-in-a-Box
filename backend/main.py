import os
import tempfile
import shutil
from typing import List, Optional
from pathlib import Path
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from .services.document_processor import DocumentProcessor
from .services.rag_service import RAGService
from .models.schemas import ChatRequest, ChatResponse, UploadResponse

app = FastAPI(title="RAG-in-a-Box", version="1.0.0")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for sessions
sessions = {}

# Initialize services
document_processor = DocumentProcessor()

@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Create temporary directory for this session
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Save uploaded file
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        chunks = await document_processor.process_document(file_path)
        
        # Initialize RAG service for this session
        rag_service = RAGService()
        await rag_service.initialize_vectorstore(chunks)
        
        # Store session
        sessions[session_id] = {
            'rag_service': rag_service,
            'temp_dir': temp_dir,
            'filename': file.filename,
            'chunks_count': len(chunks)
        }
        
        return UploadResponse(
            session_id=session_id,
            filename=file.filename,
            chunks_processed=len(chunks),
            message="Document processed successfully"
        )
        
    except Exception as e:
        # Clean up on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the uploaded document"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    rag_service = session['rag_service']
    
    try:
        response = await rag_service.query(request.message)
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and clean up resources"""
    if session_id in sessions:
        session = sessions[session_id]
        # Clean up temporary directory
        shutil.rmtree(session['temp_dir'], ignore_errors=True)
        del sessions[session_id]
        return {"message": "Session deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_sessions": len(sessions)}

# Serve static files (React build)
if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist/assets"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React app for all non-API routes"""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = Path("frontend/dist") / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        else:
            return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)