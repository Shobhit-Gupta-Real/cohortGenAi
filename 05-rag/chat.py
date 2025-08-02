from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_system",
    embedding=embeddings
)

query = input("Enter your question: ")

search_result = vector_db.similarity_search(
    query=query,
)

print(search_result)
