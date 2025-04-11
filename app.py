import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline
from sentence_transformers import SentenceTransformer
import chromadb
import json
import re
import nltk
from nltk.tokenize import sent_tokenize

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Initialize globals
summarizer_model = None
embedding_model = None
chroma_client = None
collection = None

# Load models function
def load_models():
    global summarizer_model, embedding_model, chroma_client, collection
    
    # Download nltk data if needed
    try:
        print("Checking for NLTK punkt data...")
        nltk.data.find('tokenizers/punkt')
        print("NLTK punkt data found")
    except LookupError:
        print("Downloading NLTK punkt data...")
        nltk.download('punkt', quiet=True)
        print("NLTK punkt data downloaded")
    
    # Load T5 model for summarization
    print("Loading T5 model...")
    model_name = "t5-small"  # Use smaller model for efficiency
    summarizer_model = pipeline("summarization", model=model_name)
    
    # Load Sentence Transformer for embeddings
    print("Loading Sentence Transformer model...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Initialize ChromaDB
    print("Initializing ChromaDB...")
    chroma_client = chromadb.Client()
    
    # Get or create collection
    try:
        collection = chroma_client.get_collection("research_documents")
        print(f"Collection loaded with {collection.count()} documents")
    except:
        collection = chroma_client.create_collection("research_documents")
        print("Created new empty collection")
        
    print("All models and resources loaded successfully")

# Call load_models on startup
with app.app_context():
    load_models()

def format_summary(summary_text):
    """Format the summary with headings and descriptions on separate lines"""
    # Safety check for input
    if not summary_text or not isinstance(summary_text, str):
        print("Warning: format_summary received invalid input")
        return str(summary_text) if summary_text else ""
    
    try:
        # Split into sentences
        sentences = sent_tokenize(summary_text)
        
        # Simple heuristic: First sentence is likely to be an overview/heading
        if len(sentences) <= 1:
            return summary_text
        
        formatted_summary = sentences[0] + "\n\n"  # First sentence as main heading
        
        # Process remaining sentences
        current_paragraph = []
        for sentence in sentences[1:]:
            # Heuristic to identify potential sub-headings (shorter sentences that end with a colon)
            try:
                is_heading = len(sentence) < 60 and (sentence.endswith(':') or 
                                       re.search(r'\b(key points|highlights|summary|conclusion|findings|results)\b', 
                                                 sentence.lower()))
                                                 
                if is_heading:
                    # If we have accumulated sentences, add them as a paragraph
                    if current_paragraph:
                        formatted_summary += ' '.join(current_paragraph) + "\n\n"
                        current_paragraph = []
                    
                    # Add the heading with a newline
                    formatted_summary += sentence + "\n"
                else:
                    current_paragraph.append(sentence)
            except Exception as e:
                # If any error in processing this sentence, just add it to the paragraph
                print(f"Error processing sentence in format_summary: {str(e)}")
                current_paragraph.append(sentence)
        
        # Add any remaining sentences
        if current_paragraph:
            formatted_summary += ' '.join(current_paragraph)
        
        return formatted_summary
    except Exception as e:
        print(f"Error in format_summary function: {str(e)}")
        # Return original text if formatting fails
        return summary_text

# Summarization endpoint
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    text = data['text']
    
    # Limit input text length to prevent OOM errors
    max_length = 1024  # T5-small has input length limitations
    if len(text) > max_length:
        text = text[:max_length]
    
    try:
        # Generate the summary using the model
        summary = summarizer_model(text, 
                                  max_length=150, 
                                  min_length=30, 
                                  do_sample=False)
        
        # Get the raw summary text
        raw_summary = summary[0]['summary_text']
        
        # Try formatting the summary, with error handling
        try:
            formatted_summary = format_summary(raw_summary)
        except Exception as format_error:
            print(f"Error in formatting summary: {str(format_error)}")
            # Fall back to raw summary if formatting fails
            formatted_summary = raw_summary
        
        return jsonify({
            "summary": formatted_summary,
            "raw_summary": raw_summary  # Include raw summary for backwards compatibility
        })
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in summarization: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return jsonify({"error": str(e), "traceback": error_traceback.split('\n')}), 500

# Recommendation endpoint
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    text = data['text']
    
    try:
        # Generate embedding for the query text
        query_embedding = embedding_model.encode(text)
        
        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=5
        )
        
        recommendations = []
        if results and 'documents' in results and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                try:
                    doc_data = json.loads(doc)
                    recommendations.append({
                        "title": doc_data.get("title", "Unknown Title"),
                        "url": doc_data.get("url", "#"),
                        "description": doc_data.get("description", "No description available")
                    })
                except:
                    # If doc is not valid JSON, try to extract info from text
                    recommendations.append({
                        "title": "Document " + str(i+1),
                        "url": "#",
                        "description": doc[:100] + "..." if len(doc) > 100 else doc
                    })
        
        return jsonify({
            "recommendations": recommendations
        })
    except Exception as e:
        print(f"Error in recommendation: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Citation endpoint
@app.route('/citation', methods=['POST'])
def citation():
    data = request.json
    if not data:
        return jsonify({"error": "No metadata provided"}), 400
    
    title = data.get('title', 'Unknown Title')
    authors = data.get('authors', 'Unknown Author')
    url = data.get('url', '')
    date = data.get('date', '')
    
    # Format citations
    apa = format_apa_citation(authors, title, date, url)
    mla = format_mla_citation(authors, title, date, url)
    bibtex = format_bibtex_citation(authors, title, date, url)
    
    return jsonify({
        "apa": apa,
        "mla": mla,
        "bibtex": bibtex
    })

def format_apa_citation(authors, title, date, url):
    # Basic APA format: Author. (Year, Month Day). Title. URL
    author_text = authors if authors != 'Unknown Author' else 'Anonymous'
    year = extract_year(date) if date else 'n.d.'
    return f"{author_text}. ({year}). {title}. Retrieved from {url}"

def format_mla_citation(authors, title, date, url):
    # Basic MLA format: Author. "Title." Website, Day Month Year, URL
    author_text = authors if authors != 'Unknown Author' else 'Anonymous'
    date_text = date if date else 'n.d.'
    return f"{author_text}. \"{title}.\" {date_text}. {url}"

def format_bibtex_citation(authors, title, date, url):
    # Generate a BibTeX key from the title
    key = re.sub(r'[^\w]', '', title).lower()[:20]
    year = extract_year(date) if date else 'nodate'
    
    return f"""@misc{{{key},
  title = {{{title}}},
  author = {{{authors}}},
  year = {{{year}}},
  url = {{{url}}}
}}"""

def extract_year(date_str):
    """Extract year from a date string"""
    match = re.search(r'\b(19|20)\d{2}\b', date_str)
    return match.group(0) if match else 'n.d.'

if __name__ == '__main__':
    app.run(debug=True, port=5000) 