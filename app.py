import streamlit as st
import requests


# --- Helper Functions ---
def get_transcript_languages(video_url):
    """
    Calls backend to get available transcript languages for the given YouTube video.
    Returns a list of languages.
    """
    response = requests.post("http://localhost:8000/get_languages", json={"video_url": video_url})
    if response.status_code == 200:
        return response.json().get("languages", [])
    else:
        st.error("Failed to fetch transcript languages.")
        return []



def load_transcript(video_id, language):
    """
    Calls backend to load transcript for the selected video and language.
    Returns True if successful.
    """

    try:
        response = requests.post(
            "http://localhost:8000/load_transcript",
            json={
                "video_id": video_id,
                "language": language
            }
        )

        if response.status_code == 200:

            result = response.json()

            if result.get("success"):
                return True
            else:
                st.error(result.get("error", "Transcript loading failed."))
                return False

        else:
            st.error("Backend request failed.")
            return False

    except Exception as e:
        st.error(f"Connection error: {e}")
        return False

def ask_question(video_id, language, question):
    """
    Calls backend to ask a question about the video transcript.
    Returns assistant's answer.
    """
    response = requests.post("http://localhost:8000/ask", json={
        "video_id": video_id,
        "language": language,
        "question": question
    })
    if response.status_code == 200:
        return response.json().get("answer", "")
    else:
        st.error("Failed to get answer from backend.")
        return ""

def extract_video_id(url):
    """
    Extracts YouTube video ID from URL.
    """
    import re
    match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None

# --- UI Functions ---
def show_video_input():
    """
    Step 1: User pastes YouTube video link.
    """
    st.title("YouTube RAG Chatbot")
    st.markdown("Paste a YouTube video link to get started.")
    video_url = st.text_input("YouTube Video URL", value=st.session_state.get("video_url", ""))
    submit = st.button("Submit Link")
    if submit and video_url:
        video_id = extract_video_id(video_url)
        if not video_id:
            st.error("Invalid YouTube URL.")
            return
        st.session_state.video_url = video_url
        st.session_state.video_id = video_id
        st.session_state.languages = get_transcript_languages(video_url)
        st.session_state.selected_language = None
        st.session_state.transcript_loaded = False
        st.session_state.chat_history = []
        st.rerun()

def show_language_selection():
    """
    Step 2-4: Show transcript languages dropdown and load transcript button.
    """
    st.title("Select Transcript Language")
    st.markdown(f"Video ID: {st.session_state.video_id}")
    languages = st.session_state.get("languages", [])
    if not languages:
        st.warning("No transcript languages found. Defaulting to English.")
        languages = [{"name": "English", "code": "en"}]
        st.session_state.languages = languages
    lang_names = [lang["name"] for lang in languages]
    selected_name = st.selectbox("Available Languages", lang_names, key="language_select")
    selected_code = None
    for lang in languages:
        if lang["name"] == selected_name:
            selected_code = lang["code"]
            break
    load_btn = st.button("Load Video Transcript")
    if load_btn and selected_code:
        success = load_transcript(st.session_state.video_id, selected_code)
        if success:
            st.session_state.selected_language = selected_code
            st.session_state.transcript_loaded = True
            st.rerun()
        else:
            st.error("Transcript loading failed.")

def show_chat_interface():
    """
    Step 5-7: Chat page like ChatGPT.
    """
    st.title("Chat about the Video")
    st.markdown(f"**Video ID:** {st.session_state.video_id} | **Language:** {st.session_state.selected_language}")
    chat_history = st.session_state.get("chat_history", [])
    # Display chat history
    for msg in chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div style='text-align:right; background:#e6f7ff; padding:8px; border-radius:8px; color:black; margin-bottom:4px'><b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left; background:#f6f6f6; padding:8px; border-radius:8px; color:black; margin-bottom:4px'><b>Assistant:</b> {msg['content']}</div>", unsafe_allow_html=True)
    # Input box at bottom
    with st.container():

        user_input = st.text_input(
            "Ask a question about the video...",
            key="chat_input"
        )

        if st.button("Send") and user_input:

            video_id = st.session_state.video_id
            language = st.session_state.selected_language

            answer = ask_question(video_id, language, user_input)

            st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()
# --- Main App Logic ---
# Initialize session_state variables
for key in ["video_url", "video_id", "languages", "selected_language", "transcript_loaded", "chat_history"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "chat_history" else []

# UI flow control
if not st.session_state.video_url or not st.session_state.video_id:
    show_video_input()
elif not st.session_state.transcript_loaded:
    show_language_selection()
else:
    show_chat_interface()