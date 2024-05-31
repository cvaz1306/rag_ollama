import hashlib
import streamlit as st
import PyPDF2
import chromadb
import ollama
import requests
import json
import asyncio
# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./cdb")
collection_name = "docs"
model = "gemma:2b"
# Check if the collection name exists in the list of collections
exists = collection_name in [c.name for c in client.list_collections()]
collection = client.get_or_create_collection(collection_name)
def keep_alive(model: str, keep_alive):
    url = "http://localhost:11434/api/generate"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": model,
        "keep_alive": keep_alive
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
st.info(f"Preloading Model: {model}")
keep_alive(model, -1)
def sliding_window_text(pdf_file, window_size, stride):
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        all_text = ""

        # Extract text from all pages and concatenate
        for page in pdf_reader.pages:
            text = page.extract_text()
            all_text += text
        all_text = all_text.replace(" -\n", "", -1)
        
        # Split the concatenated text into sentences
        sentences = all_text.split(". ")

        # Loop through sentences with sliding window
        window_start = 0
        while window_start + window_size <= len(sentences):
            window = sentences[window_start:window_start + window_size]
            window_text = ". ".join(window)  # Join sentences with spaces
            yield window_text
            window_start += stride

def index_pdf(path, window_size, stride, src, file_hash):
    i = 0
    for window in sliding_window_text(path, window_size, stride):
        i += 1
        collection.add(documents=[window], metadatas=[{"src": src, "file_hash": file_hash}], ids=[f"{src} {i}"])

def file_hash(file):
    hasher = hashlib.sha256()
    file.seek(0)
    buf = file.read()
    hasher.update(buf)
    return hasher.hexdigest()
async def on_query():
    st.info("Processing your query...")
    
    # Query without metadata filtering if no file is uploaded
    if uploaded_file is not None:
        # Query with metadata
        q_result = collection.query(
            query_texts=[query],
            n_results=1,
            where={"file_hash": file_id}  # Use metadata field to filter documents
        )
    else:
        # Query without file_hash filter
        q_result = collection.query(
            query_texts=[query],
            n_results=1
        )
        print(q_result)

    st.write("Query processed. Generating response...")

    # Stream the response from the model
    response_placeholder = st.empty()
    response = ""
    print(q_result['documents'][0][0])
    stream = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': f"Answer the following question using the provided text as a resource. Do not repeat or mention the text, summarize it, and synthesize a response to answer the question:\n\"{query}\"\n\n\"{q_result['documents'][0][0]}\""}],
        stream=True,
    )

    for chunk in stream:
        response += chunk['message']['content']
        print(chunk['message']['content'], end="", flush=True)
        response_placeholder.markdown(response)

    st.write("Response generated:")
    st.write(response)

st.title("PDF Query and Answer System")
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
query = st.text_input("Enter your query")

if uploaded_file is not None:
    window_size = 5
    stride = 3
    file_id = file_hash(uploaded_file)

    # Check if the file is already indexed by querying for the file hash
    existing_docs = collection.query(
        query_texts=[""], 
        n_results=1, 
        where={"file_hash": file_id}
    )
    print(len(existing_docs['documents'][0]))
    if len(existing_docs['documents'][0])<1: #not existing_docs['documents']:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        index_pdf("temp.pdf", window_size, stride, uploaded_file.name, file_id)
        st.success("PDF indexed successfully.")
    else:
        st.info("PDF already indexed.")

if query:
    asyncio.run(on_query())