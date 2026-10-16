import os
from typing import List, Tuple

import chromadb
from chromadb.config import Settings


class VectorStoreManager:
    """
    An alternative vector store using ChromaDB instead of raw numpy arrays.
    ChromaDB handles the similarity search for you and persists to disk automatically.
    NOTE: This isn't currently used by RAGPipeline — it's an alternative approach.
    """

    # This class is not currently integrated into the RAGPipeline, but it provides an alternative way to manage vector storage using ChromaDB.
    def __init__(self, persist_directory: str = "./data/vector_store"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        # Start a ChromaDB client that saves to disk
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory,
            anonymized_telemetry=False,
        )
        self.client = chromadb.Client(settings)
        self.collection = None  # Populated by create_collection()

    # Collection management (create, get)
    def create_collection(self, name: str = "warhammer_rules", embedding_function=None):
        """
        Get an existing collection or create a new one.
        A collection is like a table — it holds all the rule chunks + their vectors.
        """
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(
                name=name, embedding_function=embedding_function
            )
            print(f"Loaded existing collection: {name}")
        except:
            # Create new collection if doesn't exist
            self.collection = self.client.create_collection(
                name=name,
                embedding_function=embedding_function,
                metadata={"hnsw:space": "cosine"},  # Use cosine distance for similarity
            )
            print(f"Created new collection: {name}")

    # CRUD operations for the vector store (add, query, persist)
    def add_documents(self, documents: List[str], metadatas: List[dict], ids: List[str]):
        """Insert rule chunks into the collection so they can be searched later."""
        if self.collection is None:
            raise ValueError("Collection not initialized. Call create_collection first.")
        if not (len(documents) == len(metadatas) == len(ids)):
            raise ValueError("documents, metadatas, and ids must have the same length.")
        if not documents:
            print("No documents to add; skipping insert.")
            return

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"Added {len(documents)} documents to collection")

    # Query the vector store for relevant documents
    def query(self, query_text: str, n_results: int = 3) -> Tuple[List[str], List[dict]]:
        """Find the n most relevant rule chunks for a given question."""
        if self.collection is None:
            raise ValueError("Collection not initialized. Call create_collection first.")

        results = self.collection.query(query_texts=[query_text], n_results=n_results)

        # ChromaDB returns results nested in lists — flatten them
        documents = results["documents"][0] if results["documents"] else []
        metadatas = results["metadatas"][0] if results["metadatas"] else []

        return documents, metadatas
    
    # Persist the vector store to disk
    def persist(self):
        """Manually flush the in-memory state to disk (call before shutting down)."""
        self.client.persist()
        print("Vector store persisted to disk")
