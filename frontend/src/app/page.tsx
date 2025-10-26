"use client";

import { useState, FormEvent } from 'react';

export default function CreateCasePage() {
  const [status, setStatus] = useState({ message: '', type: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFiles(e.target.files);
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus({ message: 'Uploading and processing files... This may take a moment.', type: 'loading' });

    const formData = new FormData(e.currentTarget);

    try {
      // **IMPORTANT:** We fetch from port 5001, where your Python backend is running
      const response = await fetch('http://127.0.0.1:5001/api/create-case', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setStatus({ message: `Success! Case created. You will be redirected...`, type: 'success' });
        // Redirect to the new dashboard page (which you'll build in Phase 2)
        setTimeout(() => {
          window.location.href = `/dashboard?case_id=${result.case_id}`;
        }, 2000);
      } else {
        throw new Error(result.message || 'An unknown error occurred.');
      }
    } catch (error: any) {
      setStatus({ message: `Error: ${error.message}`, type: 'error' });
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            ⚖️ Tender for Lawyers
          </h1>
          <p className="text-slate-600 text-lg">
            AI-Powered Legal Case Management for Morgan & Morgan
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-slate-800 mb-2">
              Create a New Case
            </h2>
            <p className="text-slate-600">
              Upload case documents and our AI will automatically analyze and organize them
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Case Name Input */}
            <div>
              <label htmlFor="case-name" className="block text-sm font-medium text-slate-700 mb-2">
                Case Name
              </label>
              <input
                type="text"
                id="case-name"
                name="case_name"
                placeholder="e.g., Smith vs. Johnson Auto Accident"
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-slate-900 placeholder-slate-400"
              />
            </div>

            {/* File Upload */}
            <div>
              <label htmlFor="case-files" className="block text-sm font-medium text-slate-700 mb-2">
                Case Documents
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-slate-300 border-dashed rounded-lg hover:border-blue-400 transition-colors bg-slate-50">
                <div className="space-y-2 text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-slate-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <div className="flex text-sm text-slate-600">
                    <label
                      htmlFor="case-files"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 px-2"
                    >
                      <span>Upload files</span>
                      <input
                        id="case-files"
                        name="files"
                        type="file"
                        multiple
                        required
                        onChange={handleFileChange}
                        className="sr-only"
                      />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-slate-500">
                    PDF, TXT, JPG, PNG up to 10MB each
                  </p>
                  {selectedFiles && selectedFiles.length > 0 && (
                    <div className="mt-3 text-sm text-slate-700 bg-white rounded-lg p-3 border border-slate-200">
                      <p className="font-medium">{selectedFiles.length} file(s) selected:</p>
                      <ul className="mt-2 space-y-1 text-xs text-slate-600 text-left">
                        {Array.from(selectedFiles).map((file, idx) => (
                          <li key={idx} className="flex items-center">
                            <span className="mr-2">📄</span>
                            <span className="truncate">{file.name}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-4 px-6 rounded-lg font-semibold text-white text-lg transition-all shadow-lg ${
                isLoading
                  ? 'bg-slate-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 hover:shadow-xl active:scale-95'
              }`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing Files...
                </span>
              ) : (
                '🚀 Create Case & Analyze Documents'
              )}
            </button>
          </form>

          {/* Status Messages */}
          {status.message && (
            <div className={`mt-6 p-4 rounded-lg ${
              status.type === 'success' ? 'bg-green-50 border border-green-200' :
              status.type === 'error' ? 'bg-red-50 border border-red-200' :
              'bg-blue-50 border border-blue-200'
            }`}>
              <p className={`font-medium ${
                status.type === 'success' ? 'text-green-800' :
                status.type === 'error' ? 'text-red-800' :
                'text-blue-800'
              }`}>
                {status.type === 'success' && '✅ '}
                {status.type === 'error' && '❌ '}
                {status.type === 'loading' && '⏳ '}
                {status.message}
              </p>
            </div>
          )}
        </div>

        {/* Feature Pills */}
        <div className="mt-8 flex flex-wrap gap-3 justify-center">
          <div className="px-4 py-2 bg-white rounded-full shadow-sm border border-slate-200 text-sm text-slate-700">
            🤖 AI Document Analysis
          </div>
          <div className="px-4 py-2 bg-white rounded-full shadow-sm border border-slate-200 text-sm text-slate-700">
            🔍 Semantic Search
          </div>
          <div className="px-4 py-2 bg-white rounded-full shadow-sm border border-slate-200 text-sm text-slate-700">
            ☁️ Cloud Storage
          </div>
        </div>
      </div>
    </div>
  );
}