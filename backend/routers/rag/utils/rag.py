import os
import re
from dotenv import load_dotenv
import time
import uuid
import json

load_dotenv()
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone

# Initialize Pinecone and OpenAI embeddings
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", openai_api_key=os.environ.get("OPENAI_API_KEY")
)


def chunkify(text: str):
    """Split the text into chunks based on the ##### delimiter."""
    chunks = text.split("#####")
    documents = [
        Document(page_content=chunk.strip()) for chunk in chunks if chunk.strip()
    ]
    return documents


def ensure_index_exists():
    """Check if the index exists, and create it if it doesn't."""
    index_name = "skip-ai"
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return index_name


def embed_chunks(chunks: list, index_name: str, lecture_id: str):
    """Embed chunks and store them in Pinecone using the lecture_id as namespace."""
    PineconeVectorStore.from_documents(
        documents=chunks,
        index_name=index_name,
        embedding=embeddings,
        namespace=lecture_id,
    )
    time.sleep(1)
    return lecture_id


def namespace_exists(index_name: str, namespace: str) -> bool:
    """Check if a namespace exists in the index."""
    index = pc.Index(index_name)
    try:
        result = index.query(
            vector=[0] * 1536,  # Dummy vector for querying
            namespace=namespace,
            top_k=1,
            include_values=False,
        )
        return len(result.matches) > 0
    except Exception as e:
        return False


def query_pinecone(index_name: str, lecture_id: str):
    """Query the Pinecone index for a specific lecture and print results."""
    index = pc.Index(index_name)
    results = []
    for ids in index.list(namespace=lecture_id):
        query = index.query(
            id=ids[0],
            namespace=lecture_id,
            top_k=1,
            include_values=True,
            include_metadata=True,
        )
        results.append(query)
    return results


def process_and_post_text(text: str, lecture_id: str = None):
    """Process text through the entire pipeline and query the results."""
    chunks = chunkify(text)
    index_name = ensure_index_exists()

    # If no lecture_id is provided, generate a new one
    if not lecture_id:
        lecture_id = str(uuid.uuid4())

    if not namespace_exists(index_name, lecture_id):
        namespace = embed_chunks(chunks, index_name, lecture_id)
        print(f">>> Text processed and embedded successfully for lecture {lecture_id}.")
    else:
        print(f"Namespace {lecture_id} already exists. Skipping embedding.")

    results = query_pinecone(index_name, lecture_id)

    return lecture_id


def get_closest_snippets(query_text: str, namespace: str, top_k: int = 5):
    """
    Retrieve the X closest text snippets from the specified Pinecone namespace.

    Args:
    query_text (str): The input text to find similar snippets for.
    namespace (str): The namespace (lecture_id) to search in.
    top_k (int): The number of closest snippets to retrieve. Defaults to 3.

    Returns:
    list: A list of dictionaries containing the closest snippets and their metadata.
    """
    index_name = "skip-ai"
    index = pc.Index(index_name)

    # Generate embeddings for the query text
    query_embedding = embeddings.embed_query(query_text)

    # Query Pinecone
    results = index.query(
        vector=query_embedding,
        namespace=namespace,
        top_k=top_k,
        include_values=False,
        include_metadata=True,
    )
    return results.to_dict()


def create_excerpts(excerpts) -> str | None:
    """Combines multiple excerpts into a single string."""
    print(">>> ENTERING create_excerpts")
    matches = excerpts.get("matches")
    print(">>> matches:", matches)

    if not matches:
        return None

    result = ""
    for i, match in enumerate(matches, 1):
        text = match.get("metadata", {}).get("text", "No text available")
        result += f"excerpt {i}: {text}\n\n"

    return result.strip()

def extractTimestamps(transcript):
    # match timestamps with milliseconds
    pattern = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s-->\s(\d{2}:\d{2}:\d{2}\.\d{3})\n(.+?)\n", re.DOTALL)
    segments = pattern.findall(transcript)
    formatted_string = "\n".join(f"{start} --> {end}\n{text}" for start, end, text in segments)

    return formatted_string

# Usage
if __name__ == "__main__":
    sample_text1 = "Lecture 1: Introduction to Climate Change ##### The Earth's climate is changing rapidly ##### Human activities are the main driver"
    sample_text2 = "Lecture 2: Effects of Global Warming ##### Rising sea levels are a major concern ##### Extreme weather events are becoming more frequent"

    # Process and post each lecture separately
    lecture_id1 = process_and_post_text(sample_text1)
    lecture_id2 = process_and_post_text(sample_text2)

    # You can now query each lecture separately using their lecture_ids
    index_name = ensure_index_exists()
    print("\nQuerying Lecture 1:")
    results1 = query_pinecone(index_name, lecture_id1)
    for result in results1:
        print(result)

    print("\nQuerying Lecture 2:")
    results2 = query_pinecone(index_name, lecture_id2)
    for result in results2:
        print(result)
