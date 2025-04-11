# Curious Context Companion

A locally-hosted Chrome extension that helps with research by summarizing web pages using local AI models.

## Features

- **Page Content Extraction**: Automatically extracts text from the current web page.
- **AI-Powered Summarization**: Generates concise summaries of page content using:
  - A locally hosted T5 model (traditional approach)
  - Ollama integration (newer approach)
- **Citation Generation**: Creates citation formats (APA, MLA, BibTeX) for the current page.
- **Modern UI**: Clean interface built with React, Tailwind CSS, and shadcn/ui.

## Architecture

This project consists of two main components:

1. **Chrome Extension**: Frontend interface that captures page content and displays results.
2. **Flask Backend**: Local Python server that processes requests using AI models.

## Project Structure

```
.
├── app.py                  # Main Flask application (T5 implementation)
├── src/
│   ├── extension/          # Chrome extension files
│   │   ├── manifest.json   # Extension configuration
│   │   ├── popup.html      # Extension popup interface
│   │   ├── popup.js        # Extension popup logic
│   │   ├── background.js   # Background service worker
│   │   ├── content.js      # Content script for page extraction
│   │   └── styles.css      # Extension styles
│   ├── backend/            # Backend API implementation 
│   │   ├── app.py          # Alternate Flask app using Ollama
│   │   ├── index_corpus.py # Tool for indexing documents
│   │   └── requirements.txt # Backend dependencies
│   └── ...                 # Frontend React components
├── package.json            # Frontend dependencies
└── ...                     # Configuration files
```

## Setup Instructions

### Prerequisites

- Python 3.7+ with pip
- Chrome browser
- Node.js and npm (for frontend development)
- Ollama (optional, for alternative backend)

### Step 1: Setup the Backend

You have two options for the backend:

#### Option A: Traditional T5 Model (root app.py)

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

2. Install the required dependencies:
   ```
   pip install flask flask-cors torch transformers sentence-transformers chromadb
   ```

3. Start the Flask server:
   ```
   python app.py
   ```

#### Option B: Ollama Backend (src/backend/app.py)

1. Install [Ollama](https://ollama.ai/) and download the llama3.2 model:
   ```
   ollama pull llama3.2
   ```

2. Navigate to the backend directory:
   ```
   cd src/backend
   ```

3. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Start the Flask server:
   ```
   python app.py
   ```

### Step 2: Install the Chrome Extension

1. Open Google Chrome and navigate to `chrome://extensions/`

2. Enable "Developer mode" by toggling the switch in the top-right corner.

3. Click "Load unpacked" and select the `src/extension` directory from this project.

4. The extension should now appear in your browser toolbar.

### Step 3: (Optional) Run the React Frontend

If you want to work on the frontend components:

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

## Usage

1. Make sure the Flask backend is running (`python app.py`).

2. Browse to any web page you want to analyze.

3. Click on the extension icon in your browser toolbar.

4. The extension will:
   - Extract content from the current page
   - Request a summary from the local backend
   - Display the summary in the popup

5. You can adjust the summary length using the slider.

6. Click "Copy Summary" to copy the summary to your clipboard.

## Technical Details

### T5 Backend (app.py)
- **Summarization**: Uses the T5-small model from Hugging Face Transformers.
- **Embeddings**: Uses all-MiniLM-L6-v2 from Sentence Transformers.
- **Vector Database**: Uses ChromaDB for storing and querying document embeddings.

### Ollama Backend (src/backend/app.py)
- **Summarization**: Uses the llama3.2 model through Ollama.
- Provides a more flexible approach for different AI models.

### Frontend
- **Extension**: Plain JavaScript with a clean UI.
- **Development UI**: React with Tailwind CSS and shadcn/ui components.

## Privacy & Data

All processing happens locally on your machine:
- No data is sent to external servers or APIs
- AI models run entirely on your computer
- Your browsing data never leaves your device

## Troubleshooting

- **Extension shows "Network error"**: Make sure the Flask server is running on port 5000 (or 5001 for Ollama backend).
- **Slow performance**: The first run might be slow as models are downloaded and loaded. Subsequent runs will be faster.
- **"Backend returned an empty summary"**: Try with a different page or check the backend logs for errors.

## License

This project is licensed under the MIT License.
