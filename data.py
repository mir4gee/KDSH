from openai import OpenAI
import openai
import pathway as pw
import numpy as np
import os
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
# Set OpenAI API Key
model=SentenceTransformer("all-MiniLM-L6-v2")
def generate_embeddings(text, model=model):
    text = text.replace("\n", " ")
    embeddings=model.encode(text)
    return embeddings
# Load files into Pathway Table
def load_files_into_pathway(destination):
    rows = []
    for file_name in os.listdir(destination):
        file_path = os.path.join(destination, file_name)
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            content=""
            for page in reader.pages:
                content+=page.extract_text()            
            rows.append({"file_name": file_name, "file_content": content})
    return rows
# Create Embeddings and Storeom sentence_transformers import SentenceTransformer

# Load pre-trained Sentence Transformer model
# Free, lightweight model in Pathway VectorStore
def store_embeddings_in_index(file_table):
    embeddings = []
    file_names = []

    for row in file_table:
        file_name = row['file_name']
        text_content = row['file_content']
        # Generate embeddings for each file content
        embedding = generate_embeddings(text_content)
        
         # Only store if embedding is successfully generated
        embeddings.append(embedding)
        file_names.append(file_name)

    embeddings_np=np.array(embeddings).astype("float32")
    print(embeddings_np.shape)
    dimension=embeddings_np.shape[1]
    index=faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    print(index.ntotal)
    return index

# Main Workflow
# Specify the folder where the downloaded files are stored
downloaded_folder = "./downloaded_files"  

# Load files into Pathway Table
file_table = load_files_into_pathway(downloaded_folder)
# Generate embeddings and store them in the VectorStore
global index
index = store_embeddings_in_index(file_table)
print("Vectorstore made")
# Preview the VectorStore contents
index=index