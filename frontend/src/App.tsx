import React, { useState, useCallback } from 'react';
import { FileUpload } from './components/FileUpload';
import { ChatInterface } from './components/ChatInterface';
import { Header } from './components/Header';
import { LoadingSpinner } from './components/LoadingSpinner';
import { apiService } from './services/api';
import { FileText, MessageCircle } from 'lucide-react';

interface Session {
  sessionId: string;
  filename: string;
  chunksProcessed: number;
}

function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = useCallback(async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      const response = await apiService.uploadFile(file);
      setSession({
        sessionId: response.session_id,
        filename: response.filename,
        chunksProcessed: response.chunks_processed,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const handleNewDocument = useCallback(() => {
    if (session) {
      // Clean up current session
      apiService.deleteSession(session.sessionId).catch(console.error);
    }
    setSession(null);
    setError(null);
  }, [session]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onNewDocument={session ? handleNewDocument : undefined} />
      
      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-medium">Error:</p>
            <p>{error}</p>
          </div>
        )}

        {isUploading && (
          <div className="flex flex-col items-center justify-center py-12">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600">Processing your document...</p>
            <p className="text-sm text-gray-500">This may take a few moments</p>
          </div>
        )}

        {!session && !isUploading && (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-primary-100 rounded-full">
                  <FileText className="w-8 h-8 text-primary-600" />
                </div>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                RAG-in-a-Box
              </h1>
              <p className="text-lg text-gray-600 mb-6">
                Upload a PDF and start chatting with your document
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-500 mb-8">
                <div className="flex items-center justify-center">
                  <FileText className="w-4 h-4 mr-2" />
                  Text & Tables
                </div>
                <div className="flex items-center justify-center">
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Image Analysis
                </div>
                <div className="flex items-center justify-center">
                  <span className="w-4 h-4 mr-2 bg-green-500 rounded-full inline-block"></span>
                  Ephemeral Sessions
                </div>
              </div>
            </div>
            <FileUpload onFileUpload={handleFileUpload} />
          </div>
        )}

        {session && !isUploading && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    {session.filename}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {session.chunksProcessed} chunks processed
                  </p>
                </div>
                <div className="flex items-center text-green-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Ready
                </div>
              </div>
            </div>
            <ChatInterface sessionId={session.sessionId} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;