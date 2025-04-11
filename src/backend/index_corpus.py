
import os
import json
import argparse
import chromadb
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

def load_corpus(file_path):
    """Load corpus documents from a JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_corpus(corpus, model, batch_size=32):
    """Process corpus in batches and create embeddings"""
    chroma_client = chromadb.Client()
    
    # Get or create collection
    try:
        collection = chroma_client.get_collection("research_documents")
        print(f"Collection exists with {collection.count()} documents. Clearing...")
        chroma_client.delete_collection("research_documents")
    except:
        pass
    
    collection = chroma_client.create_collection("research_documents")
    
    # Process in batches
    total_documents = len(corpus)
    for i in tqdm(range(0, total_documents, batch_size), desc="Embedding documents"):
        batch = corpus[i:i+batch_size]
        
        # Extract data
        ids = [f"doc_{i+j}" for j in range(len(batch))]
        texts = [doc.get('text', '') for doc in batch]
        metadatas = [doc for doc in batch]
        
        # Create embeddings
        embeddings = model.encode(texts)
        
        # Store documents as JSON strings
        documents = [json.dumps(meta) for meta in metadatas]
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
        )
    
    print(f"Indexed {collection.count()} documents in ChromaDB")

def main():
    parser = argparse.ArgumentParser(description="Index documents into ChromaDB")
    parser.add_argument("--corpus", "-c", required=True,
                        help="Path to corpus JSON file")
    args = parser.parse_args()
    
    if not os.path.exists(args.corpus):
        print(f"Error: File {args.corpus} not found")
        return
    
    # Load model
    print("Loading Sentence Transformer model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Load and process corpus
    print(f"Loading corpus from {args.corpus}...")
    corpus = load_corpus(args.corpus)
    
    print(f"Processing {len(corpus)} documents...")
    process_corpus(corpus, model)
    
    print("Indexing complete!")

if __name__ == "__main__":
    main()
