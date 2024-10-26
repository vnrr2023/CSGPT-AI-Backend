from langchain_chroma import Chroma
from langchain.embeddings import HuggingFaceEmbeddings


embeddings=HuggingFaceEmbeddings()
persist_directory = "6_doc_db"
collection_name="books"
vector_store=Chroma(persist_directory=persist_directory,collection_name=collection_name, embedding_function=embeddings)

def format_query(query):
    data=vector_store.similarity_search(query=query)
    context=""
    for doc in data:
        context+=doc.page_content
    return context