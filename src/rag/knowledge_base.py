import hashlib
import pickle
from pathlib import Path

import numpy as np

from src.document_loader import DocumentLoader
from src.embeddings import EmbeddingManager


CACHE_SCHEMA_VERSION = "chunking-v2"

# Knowledge base for rule chunks and their embeddings. Uses a disk cache to speed up loading. #
class KnowledgeBase:
    """Load rule chunks and their embeddings, using a disk cache when valid."""
    # Initialize the knowledge base with the rules directory, vector store path, document loader, and embedding manager.#
    def __init__(
        self,
        rules_directory: str,
        vector_store_path: Path,
        document_loader: DocumentLoader,
        embedding_manager: EmbeddingManager,
    ):
        # Store the initialization parameters and prepare empty containers for documents, embeddings, and metadata.
        self.rules_directory = rules_directory
        self.vector_store_path = vector_store_path
        self.document_loader = document_loader
        self.embedding_manager = embedding_manager
        self.documents = []
        self.embeddings = None
        self.metadatas = []

    # Compute a hash of the rule files and the cache schema to determine if the cache is still valid.
    def _rules_hash(self) -> str:
        """Fingerprint rule files and the processing schema for cache invalidation."""
        hasher = hashlib.md5()
        hasher.update(CACHE_SCHEMA_VERSION.encode())
        rules_path = Path(self.rules_directory)
        for file_path in sorted(rules_path.rglob("*.md")):
            hasher.update(file_path.name.encode())
            hasher.update(str(file_path.stat().st_mtime_ns).encode())
        return hasher.hexdigest()

    # Initialize the knowledge base by loading a valid cache or rebuilding it from rule files.
    def initialize(self, force_rebuild: bool = False):
        """Load a valid cache or rebuild the knowledge base from rule files."""
        cache_hash_file = self.vector_store_path / "cache_hash.txt"
        embeddings_file = self.vector_store_path / "embeddings.npy"
        documents_file = self.vector_store_path / "documents.pkl"
        metadatas_file = self.vector_store_path / "metadatas.pkl"
        
        # Check if the cache is valid by comparing the current rules hash with the cached hash.
        current_hash = self._rules_hash()
        cache_valid = (
            not force_rebuild
            and cache_hash_file.exists()
            and embeddings_file.exists()
            and documents_file.exists()
            and metadatas_file.exists()
            and cache_hash_file.read_text().strip() == current_hash
        )

        # If the cache is valid, load the embeddings, documents, and metadata from the cache.   
        if cache_valid:
            print("Loading knowledge base from cache...")
            self.embeddings = np.load(str(embeddings_file))
            with open(documents_file, "rb") as file:
                self.documents = pickle.load(file)
            with open(metadatas_file, "rb") as file:
                self.metadatas = pickle.load(file)
            print(f"Loaded {len(self.documents)} documents from cache")
            return
        
        # Rebuild the knowledge base from the rule files and save it to the cache.
        print("Building knowledge base (first run or rules changed)...")
        documents, metadatas, _ids = self.document_loader.load_all_documents()
        if not documents:
            print("Warning: No documents loaded!")
            return

        self.documents = documents
        self.metadatas = metadatas

        # Store the loaded documents and metadata in the knowledge base instance.
        print("Generating embeddings...")
        embeddings_list = self.embedding_manager.embed_texts(documents)
        self.embeddings = np.array(embeddings_list)

        # Save the embeddings, documents, and metadata to the cache for future use.
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        np.save(str(embeddings_file), self.embeddings)
        with open(documents_file, "wb") as file:
            pickle.dump(self.documents, file)
        with open(metadatas_file, "wb") as file:
            pickle.dump(self.metadatas, file)
        cache_hash_file.write_text(current_hash)
        print(f"Loaded {len(documents)} documents with embeddings (cache saved)")
