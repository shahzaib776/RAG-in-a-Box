import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      if (file.type === 'application/pdf') {
        onFileUpload(file);
      }
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    multiple: false
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`upload-area ${isDragActive ? 'dragover' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center space-y-4">
          <div className="p-4 bg-gray-100 rounded-full">
            {isDragActive ? (
              <Upload className="w-8 h-8 text-primary-600" />
            ) : (
              <FileText className="w-8 h-8 text-gray-400" />
            )}
          </div>
          
          <div className="text-center">
            <p className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop your PDF here' : 'Upload a PDF document'}
            </p>
            <p className="text-gray-500">
              Drag and drop your PDF file here, or click to browse
            </p>
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-gray-400">
            <span>• Text extraction</span>
            <span>• Table analysis</span>
            <span>• Image captioning</span>
          </div>
        </div>
      </div>

      {fileRejections.length > 0 && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span className="font-medium">Upload Error</span>
          </div>
          <p className="text-red-600 text-sm mt-1">
            Please upload a valid PDF file only.
          </p>
        </div>
      )}
    </div>
  );
};