from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import ollama
import re

app = Flask(__name__)

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Store data in memory
vector_stores = {}
text_chunks_store = {}

# ------------------------------
# Utility Functions
# ------------------------------
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

# ------------------------------
# API ENDPOINTS
# ------------------------------
@app.route('/get_languages', methods=['POST'])
def get_languages():
    data = request.get_json()
    video_url = data.get('video_url')
    video_id = extract_video_id(video_url)
    if not video_id:
        error_msg = f"Invalid or missing video URL: {video_url}"
        print(f"[ERROR] {error_msg}")
        return jsonify({"error": error_msg, "languages": []}), 400
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        languages = [
            {"name": t.language, "code": t.language_code}
            for t in transcript_list
        ]
        return jsonify({
            "languages": languages,
            "video_id": video_id
        })
    except Exception as e:
        error_msg = f"Failed to fetch transcripts for video_id {video_id}: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({"error": error_msg, "languages": []}), 500

@app.route('/load_transcript', methods=['POST'])
def load_transcript():
    data = request.get_json()
    video_id = data.get('video_id')
    language = data.get('language')
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        transcript = None
        for t in transcript_list:
            if t.language_code == language:
                transcript = t.fetch()
                break
        if transcript is None:
            for t in transcript_list:
                try:
                    transcript = t.translate(language).fetch()
                    break
                except Exception:
                    continue
        if transcript is None:
            return jsonify({"success": False, "error": "Transcript not found or could not be translated."})
       
        full_text = " ".join([t.text for t in transcript])
        # Chunk transcript
        chunks = chunk_text(full_text)
        # Create embeddings
        embeddings = embed_model.encode(chunks)
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))
        # Store
        vector_stores[(video_id, language)] = index
        text_chunks_store[(video_id, language)] = chunks
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    video_id = data.get("video_id")
    language = data.get("language")
    question = data.get("question")
    index = vector_stores.get((video_id, language))
    chunks = text_chunks_store.get((video_id, language))
    if index is None:
        return jsonify({"answer": "Transcript not loaded."})
    # Embed question
    query_embedding = embed_model.encode([question])
    # Search similar chunks
    D, I = index.search(np.array(query_embedding), k=3)
    relevant_chunks = [chunks[i] for i in I[0]]
    context = "\n".join(relevant_chunks)
    prompt = f"""
Answer the question based on the context.

Context:
{context}

Question:
{question}
"""
    try:
        response = ollama.chat(
            model="phi3:mini",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["message"]["content"]
    except Exception as e:
        answer = f"Ollama error: {str(e)}"
    return jsonify({"answer": answer})

# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)