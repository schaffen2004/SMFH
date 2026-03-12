import streamlit as st
import json
import random
from pathlib import Path

st.set_page_config(page_title="QA Dataset Visualizer", layout="wide")

# Set data file path
DATA_PATH = "/home/schaffen/Workspace/Project/SMFH/data/processed/qa_context_cleaned.json"   # <-- sửa đường dẫn tại đây


# Load dataset
@st.cache_data
def load_data(path):

    text = Path(path).read_text(encoding="utf-8").strip()

    # JSONL
    if text.startswith("{"):
        data = [json.loads(line) for line in text.splitlines()]
    else:
        data = json.loads(text)

    return data

data = load_data(DATA_PATH)
total = len(data)


st.title("QA Dataset Visualizer")
st.write(f"Dataset path: `{DATA_PATH}`")
st.write(f"Total samples: **{total}**")



if "idx" not in st.session_state:
    st.session_state.idx = 0


# Define button
col1, col2, col3, col4 = st.columns([1,1,1,3])

with col1:
    if st.button("⬅ Previous"):
        st.session_state.idx = max(0, st.session_state.idx - 1)

with col2:
    if st.button("Next ➡"):
        st.session_state.idx = min(total - 1, st.session_state.idx + 1)


with col4:
    st.write(f"Sample **{st.session_state.idx+1} / {total}**")


# Slider definition
idx_slider = st.slider(
    "Jump to sample",
    0,
    total - 1,
    st.session_state.idx
)

st.session_state.idx = idx_slider
sample = data[st.session_state.idx]



# Display sample
st.subheader("Question")
st.write(sample["question"])

st.subheader("Answer")
st.write(sample["answer"])


st.subheader("Context")

contexts = sample.get("context", [])

for i, ctx in enumerate(contexts):

    with st.expander(f"Context {i+1}", expanded=True):
        st.markdown(ctx)
