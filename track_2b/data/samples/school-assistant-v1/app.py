import streamlit as st
from transformers import pipeline

chat = pipeline("text-generation", model="swiss-ai/Apertus-v1.5-8B")

st.title("School Assistant")
st.components.v1.html('<script src="https://cdn.jsdelivr.net/npm/marked@15.0.4/marked.min.js"></script>')
q = st.text_input("Your question")
if q:
    st.write(chat([{"role": "user", "content": q}], max_new_tokens=300)[0]["generated_text"][-1]["content"])
