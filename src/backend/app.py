import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import re
import nltk
from nltk.tokenize import sent_tokenize

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

def load_models():
    # Download nltk data if needed
    try:
        print("Checking for NLTK punkt data...")
        nltk.data.find('tokenizers/punkt')
        print("NLTK punkt data found")
    except LookupError:
        print("Downloading NLTK punkt data...")
        nltk.download('punkt', quiet=True)
        print("NLTK punkt data downloaded")
    
    print("Backend ready. Waiting for summarization requests.")
    pass

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

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text_to_summarize = data['text']
    max_length_hint = data.get('max_length', 150) 
    min_length_hint = data.get('min_length', 30) 
    
    # Update the prompt to encourage structured output with headings
    prompt = f"""Please provide a concise summary of the following text. Aim for a length between {min_length_hint} and {max_length_hint} words. 
    
Structure your summary with:
1. A clear main heading or overview sentence at the start
2. Use subheadings for different aspects or topics
3. Keep descriptions clear and concise
4. End with a brief conclusion if appropriate

Text:
\"\"\"
{text_to_summarize}
\"\"\"

Summary:"""

    try:
        print(f"Sending text to Ollama ({data.get('model', 'llama3.2')}) for summarization (hint: {min_length_hint}-{max_length_hint} words)...")
        
        response = ollama.chat(
            model=data.get('model', 'llama3.2'), 
            messages=[
                {'role': 'user', 'content': prompt},
            ]
        )
        
        raw_summary = response['message']['content'].strip()
        
        # Try formatting the summary, with error handling
        try:
            formatted_summary = format_summary(raw_summary)
        except Exception as format_error:
            print(f"Error in formatting summary: {str(format_error)}")
            # Fall back to raw summary if formatting fails
            formatted_summary = raw_summary
        
        print("Summary received and formatted from Ollama.")
        return jsonify({
            "summary": formatted_summary,
            "raw_summary": raw_summary  # Include raw summary for backwards compatibility
        })

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        error_type = type(e).__name__
        error_message = str(e)
        print(f"Error during Ollama summarization: {error_type}: {error_message}")
        print(f"Traceback: {error_traceback}")
        
        if 'Connection refused' in error_message or 'Failed to establish a new connection' in error_message:
            user_error = "Could not connect to local Ollama service. Please ensure Ollama is running."
            status_code = 503 
        elif 'model not found' in error_message:
             user_error = f"Ollama model specified ('{data.get('model', 'llama3.2')}') not found. Please ensure it's downloaded (e.g., 'ollama pull llama3.2')."
             status_code = 404
        elif 'context window' in error_message: 
             user_error = f"The input text is too long for the Ollama model's context window."
             status_code = 413 
        else:
            user_error = f"An unexpected error occurred during summarization: {error_message}"
            status_code = 500 
            
        return jsonify({"error": user_error, "traceback": error_traceback.split('\n')}), status_code

if __name__ == '__main__':
    print("Starting Flask server...")
    load_models() 
    app.run(debug=True, port=5001) 
