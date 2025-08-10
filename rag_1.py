from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders import UnstructuredPDFLoader
# from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
# from qdrant_client import QdrantClient

pdf_path = Path(__file__).parent / "Book.pdf"
loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()

docs = docs[:10]

# print(docs[5])

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200,
)

split_docs = text_splitter.split_documents(documents=docs)

embedder = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key="AIzaSyC0CXoXPpCYmFZGO_p4iw6Vo5cRb29ituQ"
)

# vector_store = QdrantVectorStore.from_documents(
#     documents=[],
#     url = "http://localhost:6333",
#     collection_name="Machine_learning",
#     embedding=embedder
# )

# vector_store.add_documents(documents=split_docs)

print("Injection Done")

# embedder.embed_query("Hello, World!")
# )
# print("DOCS" , len(docs))
# print("SPLIT DOCS" , len(split_docs))

retriver = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="Machine_learning",
    embedding=embedder
)

relevant_chunks = retriver.similarity_search(
    query="What is machine Learning?",
)

print("Relevant Chunks", relevant_chunks)

system_prompt = f"""
You are an helpfull AI Assistant who responds base of the available context.

Context:
{relevant_chunks}
"""