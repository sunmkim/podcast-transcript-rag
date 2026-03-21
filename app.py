import streamlit as st
from typing import List, Any
from rag.rag import RAG
from rag.constants import KNOWLEDGEBASE_ID


def get_episode_names(episodes: List, which_position: int):
    """Extract episode names from EPISODES list."""
    return [episode[which_position] for episode in episodes]


# Define available episodes
EPISODES = [
    ("13 March, 2025", "Canada's Response to Trump's Trade War", "https://www.nytimes.com/2025/03/13/podcasts/the-daily/canada-trade-war-trump.html"),
    ("19 March, 2026", "Who Is Winning the War in Iran?", "https://www.nytimes.com/2026/03/19/podcasts/the-daily/iran-war-us-israel.html")
]

st.set_page_config(page_title="Podcast Transcript RAG", layout="wide")
st.title("The DailyBot")

# Sidebar for episode selection
with st.sidebar:
    st.header("Episodes of 'The Daily' podcast from The New York Times")
    # Create display strings combining date and episode name
    episode_display = [f"{ep[0]} -- {ep[1]}" for ep in EPISODES]
    selected_display = st.selectbox(
        "Select an episode:",
        episode_display,
        index=0
    )
    # Find the full episode tuple
    selected_episode = next(ep for ep in EPISODES if f"{ep[0]} -- {ep[1]}" == selected_display)

if "rag" not in st.session_state:
    rag = RAG(KNOWLEDGEBASE_ID)
    rag.init_rag_chain()
    st.session_state.rag = rag

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_episode" not in st.session_state:
    st.session_state.selected_episode = selected_episode

# Update selected episode in session state
if st.session_state.selected_episode != selected_episode:
    st.session_state.selected_episode = selected_episode
    st.session_state.messages = []  # Clear messages when episode changes

# Display current episode with hyperlink
episode_date, episode_name, episode_url = selected_episode
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
