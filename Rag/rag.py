import os
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_FILE = os.path.join(CURRENT_DIR, "safe_claims_policy_rules_v2.txt")
CHROMA_DIR = os.path.join(CURRENT_DIR, "chroma_db")
COLLECTION_NAME = "claims_policy_rules"
SECTION_DELIMITER = "-----"


class PolicyRAG:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)

        self.embedding_function = OpenAIEmbeddingFunction(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_type="azure",
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            deployment_id=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

        # Only ingest if collection is empty
        if self.collection.count() == 0:
            chunks = self._load_and_chunk()
            self._build_db(chunks)

    def _load_and_chunk(self) -> list[dict]:
        """
        Read the policy file and split into sections using the
        '-----' lines. Each section becomes one chunk
        with its section number and title as metadata.
        """
        with open(POLICY_FILE, "r") as f:
            content = f.read()

        raw_sections = content.split(SECTION_DELIMITER)

        chunks = []
        for section in raw_sections:
            text = section.strip()

            if not text or len(text) < 20:
                continue

            # Extract section number and title from first line if present
            lines = text.split("\n")
            title = lines[0].strip() if lines else "Unknown"

            chunks.append({
                "text": text,
                "title": title,
            })

        return chunks

    def _build_db(self, chunks: list[dict]):
        """Embed and store all chunks into ChromaDB."""
        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            documents.append(chunk["text"])
            metadatas.append({
                "title": chunk["title"],
                "section_index": i
            })
            ids.append(f"section_{i}")

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Ingested {len(chunks)} policy sections into ChromaDB.")

    def query(self, question: str, n_results: int = 3) -> list[str]:
        """
        Query the policy rules collection and return the most
        relevant section texts.
        """
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results,
        )

        return results["documents"][0] if results["documents"] else []


# TEST for RAG
# if __name__ == "__main__":
#     rag = PolicyRAG()
#     print(f"Collection has {rag.collection.count()} sections.\n")

#     test_queries = [
#         "Is prior authorization required?",
#         "How are duplicate claims detected?",
#         "What are the fraud indicators?",
#     ]

#     for q in test_queries:
#         print(f"Q: {q}")
#         results = rag.query(q, n_results=2)
#         for i, r in enumerate(results):
#             print(f"  Result {i+1}: {r[:150]}...")
#         print()
