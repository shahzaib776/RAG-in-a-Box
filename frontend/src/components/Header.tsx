import React from 'react';
import { FileText, Plus } from 'lucide-react';

interface HeaderProps {
  onNewDocument?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onNewDocument }) => {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <FileText className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">RAG-in-a-Box</h1>
              <p className="text-sm text-gray-500">Multi-modal Document Q&A</p>
            </div>
          </div>
          
          {onNewDocument && (
            <button
              onClick={onNewDocument}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>New Document</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};