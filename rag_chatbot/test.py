import os
from dotenv import load_dotenv
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv(override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

embeddings = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
)

chroma_client = chromadb.CloudClient(
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE"),
    api_key=os.getenv("CHROMA_API_KEY"),
)

# Check what distance metric the collection actually uses
raw_collection = chroma_client.get_collection(name="fcps_gyn_notes")
print("Collection metadata:", raw_collection.metadata)

vectorstore = Chroma(
    client=chroma_client,
    collection_name="fcps_gyn_notes",
    embedding_function=embeddings,
)

query = "what is FEMALE PELVIS"
print(f"\nQuery: {query}\n")

# Raw distance/score, no threshold filtering
results = vectorstore.similarity_search_with_score(query, k=5)
for doc, score in results:
    section = doc.metadata.get("section_path", "?")
    print(f"score={score:.4f}  section={section}")
    print(f"  preview: {doc.page_content[:100]}...")