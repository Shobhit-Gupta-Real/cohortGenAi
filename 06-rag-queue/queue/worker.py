from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://vector-db:6333",
    collection_name="learning_system",
    embedding=embeddings
)


def process_query(query: str):
    print("searching chunks for query --- ")
    search_result = vector_db.similarity_search(
        query=query,
    )
    print(search_result)
