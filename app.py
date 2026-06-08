import streamlit as st
import pymupdf4llm
from groq import Groq
import os

# 1. Securely check for the API key in the environment variables (for deployment)
# 2. Fallback to sidebar input (for local testing/manual entry)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

st.set_page_config(page_title="AI Study Assistant", layout="wide")

if not GROQ_API_KEY:
    GROQ_API_KEY = st.sidebar.text_input("Enter Groq API Key", type="password")

st.title("🎓 AI Study Assistant")
uploaded_file = st.file_uploader("Upload your lecture PDF", type="pdf")

if uploaded_file and GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
    
    # Save/Extract PDF
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if 'md_text' not in st.session_state:
        with st.spinner("Processing PDF..."):
            st.session_state.md_text = pymupdf4llm.to_markdown("temp.pdf")
    
    tab1, tab2, tab3 = st.tabs(["📋 CBT Quiz", "🃏 Flashcards", "🤖 Ask AI"])

    with tab1:
        st.subheader("CBT Quiz Generator")
        num_questions = st.slider("Number of Questions", 1, 10, 5)
        if st.button("Generate/Refresh Quiz"):
            with st.spinner("Generating quiz..."):
                prompt = f"Create {num_questions} multiple choice questions from this text: {st.session_state.md_text[:15000]}. Format: Q, Options (A-D), Answer."
                response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.session_state.quiz_content = response.choices[0].message.content
                st.rerun()

        if 'quiz_content' in st.session_state:
            with st.form("cbt_form"):
                st.write(st.session_state.quiz_content)
                user_input = st.text_input("Your Answers (comma-separated):")
                if st.form_submit_button("Submit Quiz"):
                    st.write(f"Your answers: {user_input}")
                    st.info("Compare against the key above.")

    with tab2:
        st.subheader("Flashcards")
        if st.button("Generate Flashcards"):
            with st.spinner("Extracting concepts..."):
                prompt = f"Create 10 flashcards (Term: Definition) from this text: {st.session_state.md_text[:15000]}"
                response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.write(response.choices[0].message.content)

    with tab3:
        st.subheader("Ask the Document")
        user_q = st.text_input("Ask a question about the PDF:")
        if user_q:
            with st.spinner("Searching..."):
                prompt = f"Answer based ONLY on this text: '{user_q}'. Text: {st.session_state.md_text[:15000]}"
                response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.write(response.choices[0].message.content)

elif not GROQ_API_KEY:
    st.info("Please enter your Groq API key in the sidebar to begin.")