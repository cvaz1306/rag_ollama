import PyPDF2
import sys
import chromadb
import ollama
client = chromadb.PersistentClient(path="./cdb")
collection=None
collection_name = "science"

# Check if the collection name exists in the list of collections
exists = collection_name in [c.name for c in client.list_collections()]
print(f"[{", ".join([c.name for c in client.list_collections()])}]")
collection=client.get_or_create_collection(collection_name)

def sliding_window_text(pdf_file, window_size, stride):
  """
  This function reads a PDF file and returns a generator that yields text chunks
  of a sliding window with a specified size and stride.

  Args:
      pdf_file: Path to the PDF file.
      window_size: The size of the sliding window (number of sentences).
      stride: The number of sentences to slide the window at each step.

  Yields:
      A string containing the text within the current window.
  """
  with open(pdf_file, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    page_num = 0
    window_start = 0
    all_text = ""

    # Extract text from all pages and concatenate
    for page in pdf_reader.pages:
      text = page.extract_text()
      all_text += text
      page_num += 1
    all_text=all_text.replace(" -\n","", -1)
    # Split the concatenated text into sentences
    sentences = all_text.split(". ")

    # Loop through sentences with sliding window
    while window_start + window_size <= len(sentences):
      window = sentences[window_start:window_start + window_size]
      window_text = ". ".join(window)  # Join sentences with spaces
      yield window_text
      window_start += stride


window_size = 5
stride = 3
path="resources/"+sys.argv[1]
i=0
print(exists)
if not exists:
    for window in sliding_window_text(path, window_size, stride):
        i=i+1
        collection.add(documents=[window], metadatas=[{"src":sys.argv[1]}], ids=[f"{sys.argv[1]} {i}"])
query = " ".join(sys.argv[2:])
print("Done Indexing")
q_result=collection.query(query_texts=[query], n_results=1)
print("Done querying")
# print(q_result)
stream = ollama.chat(
    model='llama3',
    messages=[{'role': 'user', 'content': f"Answer the following question using the provided text as a resource. Do not repeat or mention the text, summarize it, and synthesize a response to answer the question:\n\"{query}\"\n\n\"{q_result}\""}],
    stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)