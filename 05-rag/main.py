from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore

load_dotenv()

file_path = Path(__file__).parent/"system.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

# text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=500   # overlap to contain some context of the previous chunk
)

split_docs = text_splitter.split_documents(documents=docs)

# Vector Embedding

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url="http://vector-db:6333",
    collection_name="learning_system",
    embedding=embeddings
)

print("Indexing of document done....")
