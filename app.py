import streamlit as st
from rag.rag import RAG
from rag.episodes import EPISODES



st.set_page_config(page_title="Podcast Transcript RAG", layout="wide")
st.title("The DailyBot")

# Sidebar for episode selection
with st.sidebar:
    st.header("Episodes of 'The Daily' podcast from The New York Times")
    # Create display strings combining date and episode name
    episode_display = [f"{ep['date']} -- {ep['title']}" for ep in EPISODES]
    selected_display = st.selectbox(
        "Select an episode:",
        episode_display,
        index=0
    )
    # Find the full episode tuple
    selected_episode = next(ep for ep in EPISODES if f"{ep['date']} -- {ep['title']}" == selected_display)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_episode" not in st.session_state:
    st.session_state.selected_episode = None

# Re-initialize RAG when episode changes or on first load
if st.session_state.selected_episode != selected_episode:
    st.session_state.selected_episode = selected_episode
    st.session_state.messages = []
    rag = RAG(selected_episode["kbid"])
    rag.init_rag_chain()
    st.session_state.rag = rag
    st.rerun()

# Display current episode with hyperlink
episode_date = selected_episode["date"]
episode_name = selected_episode["title"]
episode_url = selected_episode["url"]

with st.chat_message("assistant"):
    st.markdown(f"Hi! I am here to help you answer questions about The New York Times 'The Daily' podcast episode from {episode_date}: [{episode_name}]({episode_url})")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the podcast transcripts"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = st.session_state.rag.invoke(prompt)
        st.markdown(result["response"])

    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
