# YouTube Chatbot RAG (Retrieval-Augmented Generation)

## Project Overview
This project is an intelligent chatbot that allows users to "chat" with any YouTube video. It automatically fetches video transcripts, processes them into searchable chunks, and uses a Large Language Model (LLM) to answer questions based on the video's content.

## Features
*   Transcript Retrieval: Automatically extracts transcripts in multiple languages using the YouTube Transcript API.
*   Smart Search: Uses FAISS (Facebook AI Similarity Search) and Sentence Transformers to find relevant parts of the video.
*   AI Answers: Powered by the 'phi3:mini' model via Ollama for fast, local, and accurate responses.
*   User Interface: Built with Streamlit for a smooth, web-based experience.
*   REST API: Flask-based backend for modularity.

## Tech Stack
*   Frontend: Streamlit
*   Backend: Flask
*   LLM: Ollama (phi3:mini)
*   Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
*   Vector DB: FAISS (CPU)

## Project Structure
D:\yt-rag-chatbot
├── backend.py      # Flask API for processing transcripts & embeddings
├── app.py          # Streamlit UI for user interaction
├── .gitignore      # Prevents virtual environments from being uploaded
└── README.txt      # Project documentation

## Installation and Setup
1.  Clone the repository:
    git clone https://github.com

2.  Set up a virtual environment:
    python -m venv rag-venv
    .\rag-venv\Scripts\activate

3.  Install dependencies:
    pip install flask streamlit youtube_transcript_api sentence_transformers faiss-cpu ollama numpy

4.  Ensure Ollama is running:
    ollama run phi3:mini

## How to Run
You must run the backend and frontend in separate terminals:

Terminal 1 (Backend):
python backend.py

Terminal 2 (Frontend):
streamlit run app.py
