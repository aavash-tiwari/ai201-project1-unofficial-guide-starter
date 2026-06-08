import os

def load_documents(docs_dir="documents"):
    """Loads all text files from the specified documents directory."""
    documents = []
    if not os.path.exists(docs_dir):
        print(f"Error: Directory '{docs_dir}' does not exist.")
        return documents
        
    for filename in os.listdir(docs_dir):
        if filename.endswith(".txt") and filename != ".keep":
            file_path = os.path.join(docs_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                documents.append({
                    "text": text,
                    "game": filename  # Using 'game' field as a generic source metadata key matching standard skeletons
                })
    return documents

def clean_text(text):
    """Cleans text by removing unnecessary whitespace and basic formatting noise."""
    # Strip leading/trailing whitespaces and reduce multiple spaces/newlines to single ones
    cleaned = " ".join(text.split())
    return cleaned

def chunk_document(text, source_name, chunk_size=400, overlap=50):
    """Splits text into chunks, ensuring we don't slice a word in half."""
    cleaned = clean_text(text)
    chunks = []
    
    if len(cleaned) <= chunk_size:
        chunks.append({
            "text": cleaned,
            "game": source_name,
            "position": 0
        })
        return chunks

    start = 0
    position = 0
    while start < len(cleaned):
        end = start + chunk_size
        
        # If we are not at the end of the text, push the end index 
        # forward to the nearest space so we don't cut off a word!
        if end < len(cleaned):
            while end < len(cleaned) and cleaned[end] != ' ':
                end += 1
                
        chunk_text = cleaned[start:end].strip()
        
        chunks.append({
            "text": chunk_text,
            "game": source_name,
            "position": position
        })
        
        position += 1
        start += (chunk_size - overlap)
        
        # Adjust start to align with a word boundary too
        while start < len(cleaned) and start > 0 and cleaned[start] != ' ':
            start -= 1
            
        if start >= len(cleaned) or (len(cleaned) - start) < overlap:
            break
            
    return chunks

# Quick test execution block
if __name__ == "__main__":
    print("--- Running Ingestion & Chunking Sanity Check ---")
    docs = load_documents()
    print(f"Loaded {len(docs)} documents.")
    
    all_chunks = []
    for doc in docs:
        chunks = chunk_document(doc["text"], doc["game"])
        all_chunks.extend(chunks)
        
    print(f"Total chunks produced: {len(all_chunks)}")
    
    if all_chunks:
        print("\n--- Sample Chunk 1 ---")
        print(f"Source: {all_chunks[0]['game']}")
        print(f"Text: {all_chunks[0]['text']}")