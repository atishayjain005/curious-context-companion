
import React from 'react';

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-blue-50 to-cyan-50">
      <div className="max-w-3xl w-full p-6 bg-white rounded-lg shadow-lg">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-800 mb-3">Contextual Research Assistant</h1>
          <p className="text-lg text-gray-600">
            A locally-hosted AI research assistant that summarizes content and provides contextual recommendations
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-blue-50 p-6 rounded-lg">
            <h2 className="text-xl font-semibold text-blue-700 mb-3">Chrome Extension</h2>
            <p className="mb-4">The extension extracts content from web pages and provides AI-powered research assistance.</p>
            <ul className="list-disc pl-5 space-y-2 text-gray-700">
              <li>Summarizes web page content</li>
              <li>Finds semantically similar documents</li>
              <li>Generates citations in multiple formats</li>
              <li>All processing done locally on your machine</li>
            </ul>
          </div>

          <div className="bg-cyan-50 p-6 rounded-lg">
            <h2 className="text-xl font-semibold text-cyan-700 mb-3">Local AI Backend</h2>
            <p className="mb-4">Powered by open-source AI models that run completely on your machine.</p>
            <ul className="list-disc pl-5 space-y-2 text-gray-700">
              <li>T5 model for text summarization</li>
              <li>Sentence transformers for embeddings</li>
              <li>ChromaDB for vector search</li>
              <li>Flask API for local hosting</li>
            </ul>
          </div>
        </div>

        <div className="bg-gray-50 p-6 rounded-lg mb-8">
          <h2 className="text-xl font-semibold text-gray-700 mb-3">Getting Started</h2>
          <ol className="list-decimal pl-5 space-y-3 text-gray-700">
            <li>
              <strong>Set up the backend:</strong>
              <pre className="bg-gray-800 text-green-400 p-3 rounded mt-2 text-sm overflow-x-auto">
                cd src/backend<br />
                pip install -r requirements.txt<br />
                python index_corpus.py --corpus example_corpus.json<br />
                python app.py
              </pre>
            </li>
            <li>
              <strong>Install the Chrome extension:</strong>
              <pre className="bg-gray-800 text-green-400 p-3 rounded mt-2 text-sm overflow-x-auto">
                1. Open Chrome and go to chrome://extensions<br />
                2. Enable "Developer mode"<br />
                3. Click "Load unpacked" and select the src/extension folder
              </pre>
            </li>
            <li>
              <strong>Start researching!</strong> Click the extension icon while browsing to access AI-powered research tools.
            </li>
          </ol>
        </div>

        <footer className="text-center text-gray-500 text-sm">
          <p>A locally-hosted, privacy-focused research assistant with zero cloud dependencies</p>
          <p className="mt-2">All AI processing happens on your machine - no data is sent to external services</p>
        </footer>
      </div>
    </div>
  );
};

export default Index;
