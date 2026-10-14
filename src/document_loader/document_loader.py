import os
from pathlib import Path
from typing import List, Optional, Tuple

from src.document_loader.file_reader import RuleFileReader
from src.document_loader.text_chunker import TextChunker


class DocumentLoader:
    """Reads rule files from disk and breaks them into smaller searchable chunks."""

    # Initialize the document loader with the directory containing rule files.
    def __init__(self, rules_directory: str = "./rules"):
        self.rules_directory = rules_directory
        self.file_reader = RuleFileReader()
        self.text_chunker = TextChunker()

    # Load and chunk all documents in the rules directory.
    def load_all_documents(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> Tuple[List[str], List[dict], List[str]]:
        """Load and chunk every Markdown and text file under the rules directory."""
        documents = []
        metadatas = []
        ids = []
        doc_id_counter = 0

        # Validate chunking parameters.
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            chunk_overlap = 0
        elif chunk_overlap >= chunk_size:
            chunk_overlap = chunk_size - 1

        # Check if the rules directory exists.
        if not os.path.exists(self.rules_directory):
            print(f"Warning: Rules directory not found at {self.rules_directory}")
            return documents, metadatas, ids
        
        # Gather all Markdown and text files recursively.
        rules_root = Path(self.rules_directory)
        rule_files = sorted(list(rules_root.rglob("*.md")) + list(rules_root.rglob("*.txt")))

        # If no rule files are found, warn and return empty lists.
        if not rule_files:
            print(f"Warning: No rule files found in {self.rules_directory}")
            return documents, metadatas, ids

        # Process each rule file individually.
        for file_path in rule_files:
            relative_path = file_path.relative_to(rules_root)
            print(f"Loading: {relative_path}")
        
            content = self._read_text_file(file_path)
            if content is None:
                continue

            chunks = self._chunk_text(content, chunk_size, chunk_overlap)
            
            # Add each non-empty chunk to the documents list with metadata and a unique ID.
            for chunk in chunks:
                if chunk.strip():
                    documents.append(chunk)
                    metadatas.append({
                        "source": str(relative_path),
                        "file_path": str(file_path),
                    })
                    ids.append(f"doc_{doc_id_counter}")
                    doc_id_counter += 1

        print(f"Loaded {len(documents)} document chunks from {len(rule_files)} files")
        return documents, metadatas, ids
    
    # Read the content of a single text file safely.
    def _read_text_file(self, file_path: Path) -> Optional[str]:
        """Safely read a file. Returns None if it can't be opened or decoded."""
        return self.file_reader.read_text_file(file_path)
    
    # Chunk a single text string into smaller pieces based on the specified chunk size and overlap.
    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 100,
    ) -> List[str]:
        """Split text into chunks at Markdown heading boundaries."""
        return self.text_chunker.chunk_text(text, chunk_size, overlap)
    
    # Load a single document without chunking.
    def load_single_document(self, file_name: str) -> Tuple[List[str], List[dict], List[str]]:
        """Load just one specific file by name, without chunking."""
        file_path = Path(self.rules_directory) / file_name

        # Check if the file exists before attempting to read it.
        if not file_path.exists():
            print(f"Error: File not found at {file_path}")
            return [], [], []
        
        # Read the file content.
        content = self._read_text_file(file_path)
        if content is None:
            return [], [], []
        
        # Prepare the document, metadata, and ID lists for the single file.
        documents = [content]
        metadatas = [{"source": file_name, "file_path": str(file_path)}]
        ids = ["doc_0"]

        return documents, metadatas, ids
