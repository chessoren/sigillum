import os
import streamlit as st
from openai import OpenAI

client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key="local")

st.title("Assistant École")
q = st.text_input("Ta question")
if q:
    r = client.chat.completions.create(model="swiss-ai/Apertus-v1.5-8B", messages=[{"role": "user", "content": q}])
    st.write(r.choices[0].message.content)
